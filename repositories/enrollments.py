from data.database import insert_query, read_query
from asyncpg import UniqueViolationError
from fastapi import HTTPException

async def repo_create_enrollment(course_id, student_id, insert_data_func = insert_query):
    query = "INSERT INTO v1.enrollments (student_id, course_id) VALUES ($1,$2) RETURNING id"
    try: 
        id = await insert_data_func(query, (student_id, course_id))
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="Already enrolled in this course!")