from common.responses import Unauthorized, Forbidden
from repositories.user_repo import get_account_by_email_repo, get_user_by_id_repo
from repositories.teacher_repo import (
    update_teacher_repo,
    report_enrolled_students_repo,
    deactivate_course_repo,
    verify_email_repo,
    validate_teacher_verified_and_activated_repo
)
from typing import Union
from data.models import UserRole, TeacherResponse
from repositories.user_repo import get_role_by_email_repo
from repositories.enrollments_repo import confirm_enrollment_repo

async def get_teacher_by_email(email):
    return await get_account_by_email_repo(email, role="teacher")

async def update_teacher_service(mobile, linked_in_url, email):
        await update_teacher_repo(mobile, linked_in_url, email)
        return await get_teacher_by_email(email)

async def validate_teacher_role(email: str) -> Union[Unauthorized, Forbidden] | None:
    role = await get_role_by_email_repo(email)
    if role != UserRole.TEACHER:
        return Forbidden(content="Only a Teacher user can perform this action")
    return None

async def get_enrolled_students(teacher_id: int):
    return await report_enrolled_students_repo(teacher_id)

async def deactivate_course_service(teacher_id: int, course_id: int):
    return await deactivate_course_repo(teacher_id, course_id)

async def get_teacher_by_id(teacher_id: int):
    teacher = await get_user_by_id_repo(teacher_id, role = "teacher")
    return TeacherResponse(**teacher)

async def confirm_enrollment(enrollment_id):
     return await confirm_enrollment_repo(enrollment_id)

async def verify_email(teacher_id):
     return await verify_email_repo(teacher_id)

async def validate_teacher_verified_and_activated(teacher_id):
     validation = await validate_teacher_verified_and_activated_repo(teacher_id)
     return True if validation else False