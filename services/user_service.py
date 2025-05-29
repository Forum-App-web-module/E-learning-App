from pydantic import EmailStr

from data.database import read_query, insert_query, update_query
from security.secrets import hash_password
from data.models import RegisterData, UserRole, StudentRegisterData, TeacherRegisterData
from security.jwt_auth import verify_access_token
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from common.responses import Unauthorized, Forbidden
from repositories.user_repo import insert_user, repo_email_exists
from typing import Union

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def create_account(data: Union[TeacherRegisterData, StudentRegisterData], hashed_password: str):
    role, user_id = await insert_user(data, hashed_password)
    return role, user_id

# call repo layer email_exists
async def email_exists(email: EmailStr) -> bool:
    return await repo_email_exists(email)



# deactivates user, admin rights needed
def deactivate_user(email: str, role: UserRole, update_data_func = update_query):

    query = f"""
    UPDATE v1.{role}
    SET is_active = FALSE
    WHERE email = %s
    """
    result = update_data_func(query, (email, ))
    return result

def get_hash_by_email(email: EmailStr, get_data_func = read_query):
    query = "SELECT password FROM v1.students WHERE email = %s" \
    "UNION " \
    "SELECT password FROM v1.teachers WHERE email = %s" \
    "UNION" \
    "SELECT password FROM v1.admins WHERE email = %s"

    return get_data_func(query, (email, email, email))[0][0]

# to avoid code repetition
# check if the user role is the same as the required one
def check_user_role(token: str, role: UserRole):
    user = verify_access_token(token)
    if user.get("role") != role:
        raise Forbidden
    return True
