from services.course_service import get_course_by_id, create_course, read_all_courses

async def get_course_by_id_controller(id):
    return await get_course_by_id(id)

async def get_all_courses_controller():
    return await read_all_courses()