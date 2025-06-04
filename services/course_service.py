from repositories.course_repo import read_all_courses_per_teacher, read_course_by_id, insert_course, update_course_data, get_all_public_courses_repo, get_all_student_courses_repo
from repositories.user_repo import get_account_by_email
from common.responses import Unauthorized, NotFound
from data.models import CourseCreate, CourseUpdate
from asyncpg.exceptions import UniqueViolationError
from fastapi.exceptions import HTTPException
from repositories.enrollments import repo_create_enrollment
from typing import Optional

async def get_all_public_courses_service(tag: Optional[str]):
    return await get_all_public_courses_repo(tag)

async def get_course_by_id_service(id: int):
    return await read_course_by_id(id)

async def get_all_courses_per_teacher_service(teacher_id):
    return await read_all_courses_per_teacher(teacher_id)

async def get_all_courses_per_student_service(student_id):
    return await get_all_student_courses_repo(student_id)

async def create_course_service(course_data: CourseCreate):
    try:
        return await insert_course(course_data)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="Course with this title already axists")

async def update_course_service(id: int, updates: CourseUpdate):
    return await update_course_data(id, updates)

async def verify_course_owner(course_id: int, teacher_id: int):
    course = await read_course_by_id(course_id)

    if not course:
        return NotFound(content="Course not found")
    
    if course["owner_id"] != teacher_id:
        return Unauthorized(content="You are not the owner of the course")
    
    return True

async def enroll_course(course_id: int, student_id):
    enrollment_id = repo_create_enrollment(course_id, student_id)


async def count_premium_enrollments(student_id):
    pass