from fastapi import APIRouter
from fastapi.params import Depends
from controllers import teacher_controller
from security.auth_dependencies import get_current_user

teachers_router = APIRouter(prefix="/teachers", tags=["teachers"])


@teachers_router.get("/")
async def get_teachers(payload: str = Depends(get_current_user)):
    return await teacher_controller.get_teacher_by_email_controller(payload["sub"])

# Verify email byh email. Teacher get from email link.
@teachers_router.get("/email/{}")
async def verify_email():
    pass


