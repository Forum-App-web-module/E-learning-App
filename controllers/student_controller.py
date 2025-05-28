from services.student_service import get_student_by_email

async def get_student_by_email_controller(email):
    return await get_student_by_email(email)
