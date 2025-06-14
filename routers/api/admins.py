from fastapi import APIRouter, Depends
from security.auth_dependencies import get_current_user
from data.models import UserRole, CourseResponse, AdminCourseFilterOptions, AdminCourseListResponse
from common import responses
from config.mailJet_config import course_deprecation_email
from services.admin_service import approve_teacher, delete_course_service, get_admin_courses_view_service
from services.course_service import get_course_rating_service, get_course_by_id_service
from services.enrollment_service import unenroll_student_service



admins_router = APIRouter(prefix="/admins", tags=["admins"])

# approve teacher registration - get from email link
@admins_router.put("/teacher/{id}")
async def approve_teacher_registration(id=id, payload: dict = Depends(get_current_user)):
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")
    await approve_teacher(id)
    return responses.Successful(content=f"Teacher {id} registration is approved successfully.")

@admins_router.get("/course/{course_id}/rating")
async def get_course_rating(course_id: int, payload: dict = Depends(get_current_user)):
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")
    rating = await get_course_rating_service(course_id)
    return responses.Successful(content=rating)
    
@admins_router.put("/course/{course_id}/student/{student_id}")
async def remove_student_from_course(course_id: int, student_id: int, payload: dict = Depends(get_current_user)):
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")

    service_response = await unenroll_student_service(student_id, course_id)

    if service_response:
        return responses.Successful(content="Unenrollment successful.")
    else:
        return responses.NotFound(content="Student is not enrolled to the course.")

@admins_router.delete("/course/{course_id}")
async def delete_course(course_id: int, payload: dict = Depends(get_current_user)):
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")

    course_response = CourseResponse(**await get_course_by_id_service(course_id))

    student_emails, deleted_row_count = await delete_course_service(course_id)

    if deleted_row_count:
        email_status = await course_deprecation_email(student_emails, course_response)
        return responses.Successful(content=f"Course deleted successfully. \n Email Response: \n {email_status}")
    else:
        return responses.NotFound(content="Course not found.")
    
@admins_router.get("/courses")
async def get_admin_view_courses(filters:AdminCourseFilterOptions = Depends(), payload: dict = Depends(get_current_user)):
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")
    
    result = await get_admin_courses_view_service(
        title=filters.title,
        teacher_id=filters.teacher_id,
        student_id=filters.student_id,
        limit=filters.limit,
        offset=filters.offset
    )
    return [AdminCourseListResponse(**dict(row)) for row in result]

