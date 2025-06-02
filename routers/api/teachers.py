from fastapi import APIRouter
from fastapi.params import Depends, Header, Body
from data.models import TeacherRegisterData, UserRole, TeacherResponse
from security.auth_dependencies import get_current_user
from services.teacher_service import get_teacher_by_email, update_teacher_service
from common import responses

teachers_router = APIRouter(prefix="/teachers", tags=["teachers"])


@teachers_router.get("/")
async def get_teachers(payload: dict = Depends(get_current_user)):
    teacher = await get_teacher_by_email(payload["sub"])
    return responses.Successful(content=TeacherResponse(**teacher).model_dump(mode="json")) if teacher else responses.Forbidden(content="Only a Teacher user can perform this action")



# Verify email by email. Teacher get email from system to verify his email by clicking on the Url.
@teachers_router.get("/email/{}")
async def verify_email():
    pass


# Teacher gets email from system for course enrollments. This endpoint is sent to the teacher in the message. By clicking to the Url teacher gets this endpoint and approves.
@teachers_router.put("/enrollments/{id}")
async def approve_enrollment(payload: dict = Depends(get_current_user)):
    pass



@teachers_router.put("/")
async def update_teacher(
        payload: dict = Depends(get_current_user),
        mobile: str = Body(min_length=6, max_length=17),
        linked_in_url: str = Body(regex="^https?:\/\/www\.linkedin\.com\/.+"),
):
    email = payload["sub"]
    if not await get_teacher_by_email(email):
            return responses.NotFound(content="You need to be Teacher for this action.")
    
    teacher = await update_teacher_service(mobile, linked_in_url, email)

    return responses.Successful(content=TeacherResponse(**teacher).model_dump(mode="json"))

