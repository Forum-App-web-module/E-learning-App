
from repositories.admin_repo import approve_teacher_repo

async def approve_teacher(teacher_id):
    return await approve_teacher_repo(teacher_id)
