from repositories.course_repo import read_all_courses, read_course_by_id, insert_course, update_course_data
from common.responses import Unauthorized, NotFound
from data.models import CourseCreate, CourseUpdate

async def get_course_by_id_service(id: int):
    return await read_course_by_id(id)

async def get_all_courses_service():
    return await read_all_courses()

async def create_course_service(course_data: CourseCreate):
    return await insert_course(course_data)

async def update_course_service(id: int, updates: CourseUpdate):
    return await update_course_data(id, updates)

async def verify_course_owner(course_id: int, teacher_id: int):
    course = await read_course_by_id(course_id)

    if not course:
        raise NotFound(content="Course not found")
    
    if course["owner_id"] != teacher_id:
        raise Unauthorized(content="You are not the owner of the course")
    
    return True