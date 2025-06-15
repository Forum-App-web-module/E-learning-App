from repositories.section_repo import insert_section, update_section, get_all_course_sections_repo, hide_section_repo
from repositories.student_repo import repo_check_enrollment, repo_validate_subscription
from data.models import SectionCreate, SectionUpdate
from fastapi.exceptions import HTTPException
from asyncpg import UniqueViolationError
from repositories.course_repo import read_course_by_id

async def create_section_service(course_id: int, section: SectionCreate):
    return await insert_section(course_id, section)
    
async def get_all_sections_per_course_service(course_id, sort_by: str = "id", order: str = "asc"):
    return await get_all_course_sections_repo(course_id, sort_by, order)

async def update_section_service(course_id: int, updates: SectionUpdate):
    return await update_section(course_id, updates)

async def hide_section_service(section_id: int):
    return await hide_section_repo(section_id)
    
async def is_student_allowed_to_view_sections(course_id: int, student_id: int):
    enrolled = await repo_check_enrollment(course_id, student_id)
    if not enrolled:
        return False
    course = await read_course_by_id(course_id)
    if not course:
        return False 

    if course["is_premium"]:
        return await repo_validate_subscription(student_id)
    
    return True 