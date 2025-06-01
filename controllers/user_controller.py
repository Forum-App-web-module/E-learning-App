from data.models import StudentRegisterData, TeacherRegisterData
from typing import Union
from common.responses import Created, Unauthorized, Forbidden
from data.models import UserRole
from repositories.user_repo import repo_get_role_by_email
from services.user_service import email_exists, get_role_by_email, get_hash_by_email
from security.jwt_auth import create_access_token
from common import responses
from security.secrets import verify_password



async def validate_teacher_role(email: str) -> Union[Unauthorized, Forbidden] | None:
    role = await repo_get_role_by_email(email)
    if role != UserRole.TEACHER:
        return Forbidden(content="Only a Teacher user can perform this action")
    return None




async def authenticate_user(email: str, password: str):

    if not await email_exists(email):
        raise responses.Unauthorized("Wrong Credentials!")
    
    hashed_pw =  await get_hash_by_email(email)
    if not verify_password(password, hashed_pw):
        raise responses.Unauthorized("Wrong Credentials!")

    role = await get_role_by_email(email)

    token = create_access_token({"sub": email, "role" : role})
    
    return responses.Successful(content={"access_token": token["JWT"], "token_type": "bearer"})



