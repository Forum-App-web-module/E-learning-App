
from data.database import update_query


async def approve_teacher_repo(teacher_id, update_date_func = update_query):
    query = "UPDATE v1.teachers SET is_active = $1 WHERE id = $2"
    update = await update_date_func(query,(True, int(teacher_id)))
    return update

async def delete_course_repo(course_id, update_date_func = update_query):
    query = """
        BEGIN;

        DELETE FROM v1.course_sections WHERE course_id = $1;
        DELETE FROM v1.courses WHERE id = $1;
        
        COMMIT;
    """
    deleted_rows = await update_date_func(query, (course_id, ))

    return deleted_rows
