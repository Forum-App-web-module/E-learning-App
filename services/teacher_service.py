from common.responses import Unauthorized, Forbidden, NotFound, NoContent
from repositories.user_repo import get_account_by_email
from repositories.teacher_repo import (
    update_teacher_repo,
    report_enrolled_students,
    hide_unpopular_courses
)
from typing import Union
from data.models import UserRole
from repositories.user_repo import repo_get_role_by_email

async def get_teacher_by_email(email):
    return await get_account_by_email(email, role="teacher")

async def update_teacher_service(mobile, linked_in_url, email):
        await update_teacher_repo(mobile, linked_in_url, email)
        return await get_teacher_by_email(email)

async def validate_teacher_role(email: str) -> Union[Unauthorized, Forbidden] | None:
    role = await repo_get_role_by_email(email)
    if role != UserRole.TEACHER:
        return Forbidden(content="Only a Teacher user can perform this action")
    return None

async def get_enrolled_students(teacher_id: int):
    return await report_enrolled_students(teacher_id)

async def hide_unpopular_courses_service(teacher_id: int):
    return await hide_unpopular_courses(teacher_id)





