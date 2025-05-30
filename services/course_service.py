from repositories.course_repo import read_all_courses, read_course_by_id, insert_course, update_course_by_id
from common.responses import Unauthorized
from data.models import CourseCreate

async def get_course_by_id_service(id: int):
    return await read_course_by_id(id)

async def get_all_courses_service():
    return await read_all_courses()

async def create_course_service(course_data: CourseCreate):
    return await insert_course(course_data)

async def update_course_service():
    pass