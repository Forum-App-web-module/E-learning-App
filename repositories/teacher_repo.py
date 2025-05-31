from data.database import read_query, insert_query, update_query
from data.models import Teacher, TeacherRegisterData, UserRole
from repositories.user_repo import get_account_by_email


# account = await get_account_by_email("teacher@example.com", role="teacher")

async def update_teacher_repo(data, email):
    query = """
    UPDATE v1.teachers
    SET mobile = $1,
        linked_in_url = $2
    WHERE email = $3
    """

    return await update_query(query, (data.mobile, data.linked_in_url, email))




