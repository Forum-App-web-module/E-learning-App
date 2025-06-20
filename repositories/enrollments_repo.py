from data.database import insert_query, read_query, update_query
from datetime import datetime


async def create_enrollment_repo(course_id, student_id, insert_data_func = insert_query):
    query = """INSERT INTO v1.enrollments (student_id, course_id) 
               VALUES ($1,$2) 
               RETURNING id"""

    enrollment_id = await insert_data_func(query, (student_id, course_id))

    return enrollment_id if enrollment_id else None
    # except UniqueViolationError:
    #     raise HTTPException(status_code=400, detail="Already enrolled in this course!")

async def confirm_enrollment_repo(enrollment_id, update_data_func = update_query):
    query = """UPDATE v1.enrollments 
               SET is_approved = $1, 
                   approved_at = $2 
               WHERE id = $3"""
    timestamp = datetime.now()
    row_count = await update_data_func(query, (True, timestamp, int(enrollment_id)))
    return row_count

async def get_enrollment_by_id_repo(enrollment_id, read_data_func = read_query ):
    query = """SELECT *
               FROM v1.enrollments 
               WHERE id = $1"""
    result = await read_data_func(query, (enrollment_id,))
    return result[0] if result else None

async def get_enrollment_by_student_course_repo(student_id, course_id, read_data_func = read_query):
    query = """SELECT id 
               FROM v1.enrollments 
               WHERE student_id = $1 
                 AND course_id = $2"""
    result = await read_data_func(query, (student_id, course_id))
    return result[0] if result else None

async def unenroll_student_repo(enrollment_id: int, drop_out: bool, update_data_func = update_query):
    query = """UPDATE v1.enrollments
               SET drop_out = $2, 
                   completed_at = now() 
               WHERE id = $1"""

    row_count = await update_data_func(query, (enrollment_id, drop_out,))
    return row_count

async def unenroll_all_by_course_id_repo(course_id, update_data_func = update_query):
    query = """UPDATE v1.enrollments
               SET drop_out = $1, 
                   completed_at = now() 
               WHERE course_id = $2"""

    row_count = await update_data_func(query, (True, course_id,))
    return row_count