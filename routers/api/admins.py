from fastapi import APIRouter, Depends
from security.auth_dependencies import get_current_user
from data.models import UserRole
from common import responses
from services.admin_service import approve_teacher
from services.course_service import get_course_rating_service



admins_router = APIRouter(prefix="/admins", tags=["admins"])

# approve teacher registration - get from email link
@admins_router.put("/teacher/{id}")
async def approve_teacher_registration(id=id, payload: dict = Depends(get_current_user)):
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")
    await approve_teacher(id)
    return responses.Successful(content=f"Teacher {id} registration is approved successfully.")

@admins_router.get("/courses/{course_id}/rating")
async def get_course_rating(course_id: int, payload: dict = Depends(get_current_user)):
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")
    rating = await get_course_rating_service(course_id)
    return responses.Successful(content=rating)
    
