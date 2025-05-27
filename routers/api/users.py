from fastapi import APIRouter, Request, Header
from services.user_service import is_student, is_teacher, is_admin, check_user_role
from security.jwt_auth import get_token

users_router = APIRouter(prefix="/users", tags=["users"])

