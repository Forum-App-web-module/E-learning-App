from repositories.user_repo import get_account_by_email_repo, get_user_by_id_repo
from repositories.student_repo import (
    update_avatar_url_repo,
    update_student_data_repo,
    get_courses_student_all_repo,
    get_courses_progress_repo,
    rate_course_repo,
    allow_rating_repo, check_enrollment_repo
)
from data.models import StudentResponse
from repositories.section_repo import complete_section_repo, get_completed_sections_repo
from repositories.course_repo import complete_course_repo



async def update_student_service(first_name: str, last_name: str, avatar_url: str, user_email: str, user_role: str):
    await update_student_data_repo(first_name, last_name, avatar_url, user_email)
    return await get_account_by_email_repo(user_email, user_role)

async def get_student_courses_service(student_id: int):
    return await get_courses_student_all_repo(student_id)

async def get_student_courses_progress_service(student_id: int):
    return await get_courses_progress_repo(student_id)

async def update_avatar_url(url: str, user_email):
    return await update_avatar_url_repo(url, user_email)


async def get_student_by_email(email):
    return await get_account_by_email_repo(email, role="student")

async def rate_course_service(student_id: int, course_id: int, rating: int):
    is_allowed = await allow_rating_repo(student_id, course_id)
    print("is_allowed:", is_allowed)
    if not is_allowed:
        return None
    
    return await rate_course_repo(student_id, course_id, rating)

async def get_student_by_id(student_id: int):
    student = await get_user_by_id_repo(student_id, role = "student")
    return StudentResponse(**student).model_dump(mode="json")


async def complete_section_service(student_id: int, section_id: int):
    return await complete_section_repo(student_id, section_id)

async def complete_course_service(student_id: int, course_id: int):
    return await complete_course_repo(student_id, course_id)

async def get_completed_sections_service(course_id: int, student_id: int):
    return await get_completed_sections_repo(course_id, student_id)

async def check_enrollment_service(course_id: int, student_id: int):
    return await check_enrollment_repo(course_id, student_id)