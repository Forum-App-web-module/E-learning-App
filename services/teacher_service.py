from common.responses import Unauthorized, Forbidden, NotFound, NoContent
from repositories.user_repo import get_account_by_email
from repositories.teacher_repo import update_teacher_repo


async def get_teacher_by_email(email):
    return await get_account_by_email(email, role="teacher")

async def update_teacher_service(mobile, linked_in_url, email):
        if not await get_teacher_by_email(email):
            raise NotFound(content="User with this email does not exist")
        elif await update_teacher_repo(mobile, linked_in_url, email):
            return await get_teacher_by_email(email)
        else:
            raise NotFound(content="Oops, unfortunately, we didn't handle this outcome. No changes made")
