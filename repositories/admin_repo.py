
from data.database import update_query


async def approve_teacher_repo(teacher_id, update_date_func = update_query):
    query = "UPDATE v1.teachers SET is_active = $1 WHERE id = $2"
    update = await update_date_func(query,(True, int(teacher_id)))
    return update