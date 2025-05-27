from data.database import read_query, insert_query, update_query
from data.models import Teacher, TeacherRegisterData, UserRole
from repositories.user_repo import get_account_by_email


# account = await get_account_by_email("teacher@example.com", role="teacher")
async def get_teacher_by_email(email):
    return await get_account_by_email(email, role="teacher")

# def get_teacher_by_id():
#     pass

# def verify_teacher_email():
#     pass