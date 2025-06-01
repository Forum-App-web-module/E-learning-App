from fastapi import APIRouter
from fastapi.params import Depends, Header, Body
from controllers.teacher_controller import get_teacher_by_email_controller, update_teacher_controller
from data.models import TeacherRegisterData
from security.auth_dependencies import get_current_user


teachers_router = APIRouter(prefix="/teachers", tags=["teachers"])


@teachers_router.get("/")
async def get_teachers(payload: str = Depends(get_current_user)):
    return await get_teacher_by_email_controller(payload["sub"])

# Verify email by email. Teacher get email from system to verify his email by clicking on the Url.
@teachers_router.get("/email/{}")
async def verify_email():
    pass


# Teacher gets email from system for course enrollments. This endpoint is sent to the teacher in the message. By clicking to the Url teacher gets this endpoint and approves.
@teachers_router.put("/enrollments/{id}")
async def approve_enrollment(payload: str = Depends(get_current_user)):
    pass



@teachers_router.put("/")
async def update_teacher(
        payload: str = Depends(get_current_user),
        mobile: str = Body(min_length=6, max_length=17),
        linked_in_url: str = Body(regex="^https?:\/\/www\.linkedin\.com\/.+"),
):
    return await update_teacher_controller(mobile, linked_in_url, payload["sub"])

