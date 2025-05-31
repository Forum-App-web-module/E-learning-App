from data.models import StudentRegisterData, TeacherRegisterData
from typing import Union
from common.responses import Created, Unauthorized, Forbidden
from data.models import UserRole
from repositories.user_repo import repo_get_role_by_email

async def validate_teacher_role(email: str) -> Union[Unauthorized, Forbidden] | None:
    role = await repo_get_role_by_email(email)
    if role != UserRole.TEACHER:
        return Forbidden(content="Only a Teacher user can perform this action")
    return None







