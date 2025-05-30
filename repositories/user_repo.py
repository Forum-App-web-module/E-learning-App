from typing import Callable, Any, Union
from pydantic import EmailStr
from starlette.responses import JSONResponse

from common.responses import BadRequest
from data.database import read_query, insert_query
from data.models import StudentRegisterData, TeacherRegisterData, UserRole

ALLOWED_ROLES = {
    "student": {
        "table": "v1.students",
        "fields": "id, email, first_name, last_name, avatar_url"
    },
    "teacher": {
        "table": "v1.teachers",
        "fields": "id, email, mobile, linked_in_url"
    },
}

async def insert_user(user_data: Union[StudentRegisterData, TeacherRegisterData], hashed_password: str):

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

async def repo_email_exists(email: EmailStr, get_data_func = read_query) -> bool:

    query = """
            SELECT email FROM v1.students
                WHERE email = $1
            UNION
            SELECT email FROM v1.teachers
                WHERE email = $2
            """
    result = await get_data_func(query, (email, email))
    return bool(result)


async def get_account_by_email(
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

async def repo_get_role_by_email(email, get_data_func: Callable[[str, tuple], Any] = read_query):

    tables = {"v1.students": "student", "v1.teachers": "teacher", "v1.admins": "admins"}
    query = "SELECT 1 FROM v1.students WHERE email = $1"

    for table, role in tables.items():
        query = f"SELECT 1 FROM {table} WHERE email = $1"
        role_found = get_data_func(query,(email,))
        if role_found:
            return role



