from repositories.user_repo import get_account_by_email


from data.database import insert_query, update_query




def update_avatar_url(url: str, user_email, update_data_func = update_query):
    query = "UPDATE v1.students SET avatar_url = %s WHERE email = %s"
    id = update_query(query, (url, user_email))
    return id
# account = await get_account_by_email("student@example.com", role="student")

async def get_student_by_email(email):
    return await get_account_by_email(email, role="student")