from starlette.responses import JSONResponse

from services.teacher_service import get_teacher_by_email, update_teacher_service
from typing import Union
from common.responses import Created, Unauthorized, Forbidden, NoContent, NotFound
from data.models import UserRole
from repositories.user_repo import repo_get_role_by_email

# Teacher Role validation - call repo
async def validate_teacher_role(email: str) -> Union[Unauthorized, Forbidden] | None:
    role = await repo_get_role_by_email(email)
    if role != UserRole.TEACHER:
        return Forbidden(content="Only a Teacher user can perform this action")
    return None

async def get_teacher_by_email_controller(email: str):
    return await get_teacher_by_email(email)

async def update_teacher_controller(mobile, linked_in_url, email):
        await validate_teacher_role(email)
        return await update_teacher_service(mobile, linked_in_url, email)









