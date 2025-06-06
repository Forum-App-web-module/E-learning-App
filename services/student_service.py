from repositories.user_repo import get_account_by_email
from data.database import insert_query, update_query
from repositories.student_repo import (
    repo_update_avatar_url,
    update_student_data,
    repo_get_courses_student_all,
    repo_get_courses_progress,
    repo_rate_course,
    repo_allow_rating
)



async def update_student_service(first_name: str, last_name: str, avatar_url: str, user_email: str, user_role: str):
    await update_student_data(first_name, last_name, avatar_url, user_email)
    return await get_account_by_email(user_email, user_role)

async def get_student_courses_service(student_id: int):
    return await repo_get_courses_student_all(student_id)

async def get_student_courses_progress_service(student_id: int):
    return await repo_get_courses_progress(student_id)

async def update_avatar_url(url: str, user_email):
    return await repo_update_avatar_url(url, user_email)


async def get_student_by_email(email):
    return await get_account_by_email(email, role="student")

async def rate_course_service(student_id: int, course_id: int, rating: int):
    is_allowed = await repo_allow_rating(student_id, course_id)
    print("is_allowed:", is_allowed)
    if not is_allowed:
        return None
    
    return await repo_rate_course(student_id, course_id, rating)

