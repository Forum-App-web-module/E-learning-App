from services.teacher_service import get_teacher_by_email, update_teacher_service
from typing import Union
from common.responses import Unauthorized, Forbidden
from data.models import UserRole
from repositories.user_repo import get_role_by_email_repo
from services.course_service import get_course_by_id_repo
from services.student_service import get_student_by_email
from fastapi import HTTPException

# Teacher Role validation - call repo
async def validate_teacher_role(email: str) -> Union[Unauthorized, Forbidden] | None:
    role = await get_role_by_email_repo(email)
    if role != UserRole.TEACHER:
        return Forbidden(content="Only a Teacher user can perform this action")
    return None

async def get_teacher_id(email):
    teacher = await get_teacher_by_email(email)
    if not teacher:
        return Unauthorized(content="Only accessible for teachers!")
    return teacher["id"]

async def get_student_id(email):
    student = await get_student_by_email(email)
    if not student:
        return Unauthorized(content="Only accessible for student!")
    return student["id"]


async def verify_course_owner(course_id: int, teacher_id: int):
    course = await get_course_by_id_repo(course_id)

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course["owner_id"] != teacher_id:
        raise HTTPException(status_code=403, detail="Only course onwer is allowed to perform this action")
    
    return True


    

     







