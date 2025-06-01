from data.database import insert_query, read_query



async def repo_create_enrollment(course_id, student_id, insert_data_func = insert_query):
    query = "INSERT INTO v1.enrollments (student_id, course_id) VALUES ($1,$2) RETURNING id"
    id = await insert_data_func(query, (student_id, course_id))
    return id