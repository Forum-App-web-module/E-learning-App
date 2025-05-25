from fastapi import APIRouter
from data.models import LoginData, StudentRegisterData, TeacherRegisterData, UserRole
from services.user_service import email_exists, create_account
from common import responses
from typing import Union
from security import secrets

auth_router = APIRouter(prefix="", tags=["Auth"])

@auth_router.post('/login')
def login(login: LoginData):
    pass

@auth_router.post('/register')
def register(register_data: Union[StudentRegisterData, TeacherRegisterData]):
    if email_exists(register_data.email):
        return responses.BadRequest(content="Email already registered.")
    
    role, role_id = create_account(register_data, secrets.hash_password(register_data.password))

    return responses.Created(content={
        "message": f"New User is registered.",
        "role": role.value,
        "id": role_id
    })

    