from starlette.responses import JSONResponse
from services.teacher_service import get_teacher_by_email, update_teacher_service
from typing import Union
from common.responses import Created, Unauthorized, Forbidden, NoContent, NotFound
from data.models import UserRole
from repositories.user_repo import repo_get_role_by_email
from services.course_service import get_all_courses_per_teacher_service

# Teacher Role validation - call repo
async def validate_teacher_role(email: str) -> Union[Unauthorized, Forbidden] | None:
    role = await repo_get_role_by_email(email)
    if role != UserRole.TEACHER:
        return Forbidden(content="Only a Teacher user can perform this action")
    return None

# async def verify_teacher_id(email):
#     teacher = await get_teacher_by_email(email)
#     if not teacher["id"]:
#         return Unauthorized(content="Only accessible for teachers!")
#     return teacher["id"]
#
# async def get_all_courses_controller(email):
#     if isinstance(await validate_teacher_role(email), Forbidden):
#         return Forbidden(content="Only a Teacher user can perform this action")
#
#     teacher_id = await verify_teacher_id(email)
#     return await get_all_courses_per_teacher_service(teacher_id)
    

     







