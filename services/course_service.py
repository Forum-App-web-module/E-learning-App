from repositories.course_repo import (
    get_all_courses_per_teacher_repo, get_course_by_id_repo, insert_course_repo, update_course_data_repo, get_all_courses_repo,
    get_all_student_courses_repo, count_premium_enrollments_repo, get_course_rating_repo)
from repositories.student_repo import validate_subscription_repo
from data.models import CourseCreate, CourseUpdate, CourseFilterOptions, StudentCourseFilter, TeacherCourseFilter
from asyncpg.exceptions import UniqueViolationError
from fastapi.exceptions import HTTPException
from repositories.enrollments_repo import create_enrollment_repo
from typing import Optional

async def get_all_courses_service(filters: CourseFilterOptions, student_id: Optional[int] = None):
    premium = False
    if student_id:
        premium = await validate_subscription_repo(student_id)
    return await get_all_courses_repo(filters, premium)

async def get_course_by_id_service(id: int):
    return await get_course_by_id_repo(id)

async def get_all_courses_per_teacher_service(teacher_id, filters: TeacherCourseFilter):
    return await get_all_courses_per_teacher_repo(teacher_id, filters)

async def get_all_courses_per_student_service(student_id, filters: StudentCourseFilter):
    return await get_all_student_courses_repo(student_id, filters)

async def create_course_service(course_data: CourseCreate):
    try:
        return await insert_course_repo(course_data)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="Course with this title already exists")

async def update_course_service(id: int, updates: CourseUpdate):
    return await update_course_data_repo(id, updates)


async def enroll_course(course_id: int, student_id: int):
    enrollment_id = await create_enrollment_repo(course_id, student_id)
    return enrollment_id


async def count_premium_enrollments(student_id):
    return await count_premium_enrollments_repo(student_id)

async def get_course_rating_service(course_id: int):
    data = await get_course_rating_repo(course_id) 
    return [dict(row) for row in data] 