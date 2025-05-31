from repositories.course_repo import insert_section
from repositories.user_repo import get_account_by_email
from data.models import SectionCreate
from fastapi.exceptions import HTTPException
from asyncpg import UniqueViolationError

async def create_section_service(course_id: int, section: SectionCreate):
    try:
        return await insert_section(course_id, section)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="Section with this title already axists")
    
   