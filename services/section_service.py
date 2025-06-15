from repositories.section_repo import insert_section_repo, update_section_repo, get_all_course_sections_repo, hide_section_repo
from repositories.student_repo import check_enrollment_repo, validate_subscription_repo
from data.models import SectionCreate, SectionUpdate
from repositories.course_repo import get_course_by_id_repo

async def create_section_service(course_id: int, section: SectionCreate):
    return await insert_section_repo(course_id, section)
    
async def get_all_sections_per_course_service(course_id, sort_by: str = "id", order: str = "asc"):
    return await get_all_course_sections_repo(course_id, sort_by, order)

async def update_section_service(course_id: int, updates: SectionUpdate):
    return await update_section_repo(course_id, updates)

async def hide_section_service(section_id: int):
    return await hide_section_repo(section_id)
    
async def is_student_allowed_to_view_sections(course_id: int, student_id: int):
    enrolled = await check_enrollment_repo(course_id, student_id)
    if not enrolled:
        return False
    course = await get_course_by_id_repo(course_id)
    if not course:
        return False 

    if course["is_premium"]:
        return await validate_subscription_repo(student_id)
    
    return True 