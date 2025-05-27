from services.teacher_service import get_teacher_by_email

async def get_teacher_by_email_controller(email):
    return await get_teacher_by_email(email)