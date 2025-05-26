from fastapi import APIRouter, Request, Header
from services.user_service import is_student, is_teacher, is_admin
from security.jwt_auth import get_token

users_router = APIRouter(prefix="/auth", tags=["Role Checks"])


@users_router.get("/check/student") #TODO to be renamed
def check_student(token: str = Header(...)):
    """
Checks if a user is a student \n
Retrieves a valid token \n
Returns dict with user data if True

    """
    if is_student(token):
        return {"detail": "User is a student"}