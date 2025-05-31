from repositories.user_repo import get_account_by_email
from data.database import insert_query, update_query
from repositories.student_repo import repo_update_avatar_url
from data.models import StudentResponse


async def update_avatar_url(url: str, user_email):
    return await repo_update_avatar_url(url, user_email)

# account = await get_account_by_email("student@example.com", role="student")
async def get_student_by_email(email):
    student_atributes = await get_account_by_email(email, role="student")
    if student_atributes:
        student_profile = StudentResponse(*student_atributes)
        return student_profile
    return None