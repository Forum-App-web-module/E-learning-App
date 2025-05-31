from fastapi import APIRouter
from fastapi.params import Depends, Header, Body
from controllers.teacher_controller import get_teacher_by_email_controller, update_teacher_controller
from data.models import TeacherRegisterData
from security.auth_dependencies import get_current_user


teachers_router = APIRouter(prefix="/teachers", tags=["teachers"])


@teachers_router.get("/")
async def get_teachers(payload: str = Depends(get_current_user)):
    return await get_teacher_by_email_controller(payload["sub"])

# Verify email byh email. Teacher get from email link.
@teachers_router.get("/email/{}")
async def verify_email():
    pass

@teachers_router.put("/")
async def update_teacher(
        payload: str = Depends(get_current_user),
        mobile: str = Body(min_length=6, max_length=17),
        linked_in_url: str = Body(regex="^https?:\/\/www\.linkedin\.com\/.+"),
):
    return await update_teacher_controller(mobile, linked_in_url, payload["sub"])

