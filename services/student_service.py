from repositories.user_repo import get_account_by_email


# account = await get_account_by_email("student@example.com", role="student")

async def get_student_by_email(email):
    return await get_account_by_email(email, role="student")