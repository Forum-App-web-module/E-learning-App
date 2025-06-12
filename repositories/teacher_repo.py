from data.database import read_query, insert_query, update_query



async def update_teacher_repo(mobile, linked_in_url, email, update_data_func = update_query):
    query = """
        UPDATE v1.teachers
        SET mobile = COALESCE($1, mobile),
            linked_in_url = COALESCE($2, linked_in_url)
        WHERE email = $3
    """

    result = await update_data_func(query, (mobile, linked_in_url, email))
    return result if result else None

async def report_enrolled_students(owner_id: int,  get_data_func = read_query):
    query = """
        SELECT e.student_id, s.email, s.first_name, s.last_name,
           e.course_id, c.title, e.requested_at, e.approved_at, e.completed_at, e.drop_out, c.created_on
        FROM v1.enrollments AS e
            JOIN v1.courses AS c
        ON e.course_id = c.id
            JOIN v1.students AS s
        ON e.student_id = s.id
        WHERE c.owner_id = $1
    """

    report = await get_data_func(query, (owner_id, ))
    return report if report else None

async def hide_unpopular_courses(teacher_id: int, update_data_func = update_query):
    query = """
        UPDATE v1.courses c
        SET is_hidden = true
        WHERE owner_id = $1
        AND NOT EXISTS (
            SELECT 1
            FROM v1.enrollments e
            WHERE e.course_id = c.id
        )
    """

    result = await update_data_func(query, (teacher_id, ))
    return result if result else None

