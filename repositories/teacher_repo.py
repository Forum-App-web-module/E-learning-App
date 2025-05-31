from data.database import read_query, insert_query, update_query


# account = await get_account_by_email("teacher@example.com", role="teacher")

async def update_teacher_repo(mobile, linked_in_url, email):
    query = """
    UPDATE v1.teachers
    SET mobile = $1,
        linked_in_url = $2
    WHERE email = $3
    """

    return await update_query(query, (mobile, linked_in_url, email))




