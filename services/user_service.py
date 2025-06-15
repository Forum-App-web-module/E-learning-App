from pydantic import EmailStr
from data.database import read_query, update_query
from data.models import UserRole, StudentRegisterData, TeacherRegisterData
from fastapi.security import OAuth2PasswordBearer
from repositories.user_repo import insert_user_repo, email_exists_repo, get_role_by_email_repo
from typing import Union

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def create_account(data: Union[TeacherRegisterData, StudentRegisterData], hashed_password: str):
    role, user_id = await insert_user_repo(data, hashed_password)
    return role, user_id

# call repo layer email_exists
async def email_exists(email: EmailStr) -> bool:
    return await email_exists_repo(email)


# deactivates user, admin rights needed
def deactivate_user(email: str, role: UserRole, update_data_func = update_query):

    query = f"""
    UPDATE v1.{role}
    SET is_active = FALSE
    WHERE email = %s
    """
    result = update_data_func(query, (email, ))
    return result

async def get_hash_by_email(email: EmailStr, get_data_func = read_query):
    query = "SELECT password FROM v1.students WHERE email = $1 " \
    "UNION " \
    "SELECT password FROM v1.teachers WHERE email = $2 " \
    "UNION " \
    "SELECT password FROM v1.admins WHERE email = $3"

    result = await get_data_func(query, (email, email, email))

    return result[0][0]


async def get_role_by_email(email):
    return await get_role_by_email_repo(email)
