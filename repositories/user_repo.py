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

async def get_role_by_email_repo(email, get_data_func: Callable[[str, tuple], Any] = read_query):

    tables = {"v1.students": "student", "v1.teachers": "teacher", "v1.admins": "admin"}
    
    for table, role in tables.items():
        query = f"SELECT 1 FROM {table} WHERE email = $1"
        role_found = await get_data_func(query,(email,))
        if role_found:
            return role
    else:
        return None

async def get_user_by_id_repo(user_id, role: str, get_data_func: Callable[[str, tuple], Any] = read_query
):
    role_info = ALLOWED_ROLES.get(role.lower())

    query = f"""
        SELECT {role_info['fields']}
        FROM {role_info['table']}
        WHERE id = $1
    """

    result = await get_data_func(query, (user_id,))
    return result[0] if result else None

