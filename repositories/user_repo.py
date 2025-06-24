from typing import Callable, Any, Union
from pydantic import EmailStr
from common.responses import BadRequest
from data.database import read_query, insert_query
from data.models import StudentRegisterData, TeacherRegisterData, UserRole

ALLOWED_ROLES = {
    "student": {
        "table": "v1.students",
        "fields": "id, email, first_name, last_name, avatar_url, is_active, notifications"
    },
    "teacher": {
        "table": "v1.teachers",
        "fields": "id, email, mobile, linked_in_url, is_active"
    },
    "admin": {
        "table": "v1.admins",
        "fields": "id, email"
    },
}

async def insert_user_repo(user_data: Union[StudentRegisterData, TeacherRegisterData], hashed_password: str):
    """
    Insert user data into the database based on the user type and return
    the associated role and user ID.

    This function handles the insertion of both student and teacher user data
    into their respective database tables. It determines the type of user and
    executes the corresponding query with the provided hashed password and
    additional user-specific information. An exception is returned if the
    provided user data type is not recognized.

    :param user_data: An instance of either StudentRegisterData or
        TeacherRegisterData containing user details to be inserted.
    :type user_data: Union[StudentRegisterData, TeacherRegisterData]
    :param hashed_password: The hashed password to be saved for the user.
    :type hashed_password: str
    :return: A tuple where the first element is the user's role
        (UserRole.STUDENT or UserRole.TEACHER), and the second element
        is the newly created user ID.
    :rtype: Tuple[UserRole, int]
    """

    if isinstance(user_data, StudentRegisterData):
        query = """
            INSERT INTO v1.students (email, password)
            VALUES ($1, $2)
            RETURNING id
        """
        values = (user_data.email, hashed_password)
        role = UserRole.STUDENT

    elif isinstance(user_data, TeacherRegisterData):
        query = """
            INSERT INTO v1.teachers (email, password, mobile, linked_in_url)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        values = (user_data.email, hashed_password, user_data.mobile, user_data.linked_in_url)
        role = UserRole.TEACHER

    else:
        return BadRequest("Unknown user data type")

    user_id = await insert_query(query, values)
    return role, user_id

async def email_exists_repo(email: EmailStr, get_data_func = read_query) -> bool:
    """
    Checks the existence of an email in multiple user tables within a database.

    This function queries the database to determine if a given email exists in
    any of the 'students', 'teachers', or 'admins' tables. The function uses
    an asynchronous data fetching function, which can be customized by the
    caller. The function returns a boolean value indicating whether the email
    exists in at least one of the tables.

    :param email: The email address to check in the database.
    :type email: EmailStr
    :param get_data_func: The asynchronous function to execute the database
        query. Defaults to `read_query`.
    :type get_data_func: Callable[[str, tuple], Awaitable[Any]]
    :return: A boolean indicating whether the email exists in any user table.
    :rtype: bool
    """

    query = """
        SELECT email FROM v1.students
            WHERE email = $1
        UNION
        SELECT email FROM v1.teachers
            WHERE email = $2
        UNION
        SELECT email FROM v1.admins
            WHERE email = $3
    """
    result = await get_data_func(query, (email, email, email))
    return bool(result)


async def get_account_by_email_repo(
    email: str,
    role: str,
    get_data_func: Callable[[str, tuple], Any] = read_query
):
    """
    Retrieve account information by email and role from the database.

    This function fetches the account details from a specific table
    mapped to the provided role. It validates the `role` parameter
    against allowed roles and dynamically constructs a query to fetch
    the relevant data for the provided email. If the role is not
    supported, an exception is raised.

    :param email: The email address of the account to retrieve.
    :type email: str
    :param role: The role associated with the account (e.g., 'admin', 'user').
    :type role: str
    :param get_data_func: A callable function that executes a database query.
                          Defaults to 'read_query'.
    :type get_data_func: Callable[[str, tuple], Any]
    :return: The first matching account record, or None if no match is found.
    :rtype: Any
    :raises ValueError: If the provided role is not in the allowed roles.
    """
    role_info = ALLOWED_ROLES.get(role.lower())

    if not role_info:
        raise ValueError(f"Unsupported role: {role}")

    query = f"""
        SELECT {role_info['fields']}
        FROM {role_info['table']}
        WHERE email = $1
    """

    result = await get_data_func(query, (email,))
    return result[0] if result else None

async def get_role_by_email_repo(
        email,
        get_data_func: Callable[[str, tuple], Any] = read_query
):
    """
    Retrieves the role associated with a given email by querying specified database tables. The function
    executes queries on tables corresponding to students, teachers, and admins, and returns the matching role
    if found. If no role is associated with the email, it returns None.

    :param email: The email address to search for in the database.
    :type email: str
    :param get_data_func: A callable function that executes queries. Defaults to `read_query`.
    :type get_data_func: Callable[[str, tuple], Any]
    :return: The associated role of the email ("student", "teacher", or "admin") if found; otherwise, None.
    :rtype: Optional[str]
    """

    tables = {"v1.students": "student", "v1.teachers": "teacher", "v1.admins": "admin"}
    
    for table, role in tables.items():
        query = f"SELECT 1 FROM {table} WHERE email = $1"
        role_found = await get_data_func(query,(email,))
        if role_found:
            return role
    else:
        return None

async def get_user_by_id_repo(
        user_id,
        role: str,
        get_data_func: Callable[[str, tuple], Any] = read_query
):
    """
    Fetches a user by their unique identifier from a database repository based on the given role.

    This function retrieves the specific fields of a user from the appropriate table
    based on the role provided. The role is used to determine the correct table and
    fields via a predefined mapping. The function executes the query asynchronously
    using the provided data retrieval callable.

    :param user_id: The unique identifier of the user to retrieve.
    :type user_id: Any
    :param role: The role of the user, used to determine the database table and fields to query.
    :type role: str
    :param get_data_func: A callable function for executing the database read operation. Defaults to `read_query`.
    :type get_data_func: Callable[[str, tuple], Any]
    :return: The first record of the retrieved user data or None if no record is found.
    :rtype: Any
    """
    role_info = ALLOWED_ROLES.get(role.lower())

    query = f"""
        SELECT {role_info['fields']}
        FROM {role_info['table']}
        WHERE id = $1
    """

    result = await get_data_func(query, (user_id,))
    return result[0] if result else None

