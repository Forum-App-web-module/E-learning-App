
from repositories.admin_repo import approve_teacher_repo, delete_course_repo
from repositories.teacher_repo import report_enrolled_students
from repositories.course_repo import read_course_by_id

async def approve_teacher(teacher_id):
    return await approve_teacher_repo(teacher_id)

async def delete_course_service(course_id: int):
    course_data = await read_course_by_id(course_id)
    if course_data:
        owner_id = course_data["owner_id"]
        enrolled_students_data = await report_enrolled_students(owner_id)
        deleted_row_count = await delete_course_repo(course_id)
        student_emails = [row["email"] for row in enrolled_students_data]

        return student_emails, deleted_row_count
    else:
        return None, None





