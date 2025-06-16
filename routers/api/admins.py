from fastapi import APIRouter, Depends
from security.auth_dependencies import get_current_user
from data.models import UserRole, CourseResponse, AdminCourseFilterOptions, AdminCourseListResponse, Action, Action_UserRole
from common import responses
from config.mailJet_config import course_deprecation_email, notify_user_for_account_state
from services.admin_service import get_admin_courses_view_service, soft_delete_course_service, change_account_state
from services.course_service import get_course_rating_service, get_course_by_id_service
from services.enrollment_service import unenroll_student_service
from services.teacher_service import get_teacher_by_id
from services.student_service import get_student_by_id


admins_router = APIRouter(prefix="/admins", tags=["admins"])

# Used also for approve teacher registration - URL received on email after teacher registration.
@admins_router.put("/{role}/{action}/{id}")
async def Activate_or_Deactivate_user_account(role: Action_UserRole, action: Action, id: int, payload: dict = Depends(get_current_user)):
    """
    Activate or deactivate a user account - teacher or student.\n
    Available for admins only.

    """
    # Admin authorization validation
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")
    
    state_change = await change_account_state(role, action, id)
    if state_change:
        if role == Action_UserRole.teacher:
            user_object = await get_teacher_by_id(teacher_id = id)
        else: user_object= await get_student_by_id(student_id = id)
        await notify_user_for_account_state(action=action, role=role, user_email=user_object.get("email"))
        return responses.Successful(content=f"{role.value.upper()} with ID:{id} is {action.value.upper()+"D"} successfully.") 
    return responses.NotFound(content=f"There is no {role.value.upper()} with ID:{id}")


@admins_router.get("/course/{course_id}/rating")
async def get_course_rating(course_id: int, payload: dict = Depends(get_current_user)):
    """
    Returns all ratings for a specific course. \n
    Admin access required.
    """
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")
    rating = await get_course_rating_service(course_id)
    return responses.Successful(content=rating)
    
@admins_router.put("/course/{course_id}/student/{student_id}")
async def remove_student_from_course(course_id: int, student_id: int, payload: dict = Depends(get_current_user)):
    """
    Unenroll a student from a course.\n
    Admin access required.
    """
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")

    service_response = await unenroll_student_service(student_id, course_id)

    if service_response:
        return responses.Successful(content="Unenrollment successful.")
    else:
        return responses.NotFound(content="Student is not enrolled to the course.")

@admins_router.patch("/course/{course_id}")
async def soft_delete_course(course_id: int, payload: dict = Depends(get_current_user)):
    """
    Hides the course and notifies students.\n
    Admin access required.
    """
    if not payload["role"] == UserRole.ADMIN:
        return responses.Forbidden(content="Admin authorisation required.")

    course_response = CourseResponse(**await get_course_by_id_service(course_id))


    student_emails, deleted_row_count = await soft_delete_course_service(course_id)

    if deleted_row_count:
        email_status = await course_deprecation_email(student_emails, course_response)
        return responses.Successful(content=f"Course deleted successfully. \n Email Response: \n {email_status}")
    else:
        return responses.NotFound(content="Course not found.")
    
@admins_router.get("/courses")
async def get_admin_view_courses(filters:AdminCourseFilterOptions = Depends(), payload: dict = Depends(get_current_user)):
    """
    View all courses with filters (title, teacher, student).\n
    Admin access required.
    """
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

