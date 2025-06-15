
from repositories.admin_repo import change_account_state_repo, delete_course_repo
from repositories.teacher_repo import report_enrolled_students
from repositories.course_repo import read_course_by_id, admin_course_view_repo
from data.models import Action_UserRole, Action

async def change_account_state(role: Action_UserRole, action: Action, user_id: int):
    change = await change_account_state_repo(role, action, user_id)
    return change if change else None


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

async def get_admin_courses_view_service(
        title: str = "",
        teacher_id: int = None,
        student_id: int = None,
        limit: int = 5,
        offset: int = 0):
    return await admin_course_view_repo(title, teacher_id, student_id, limit, offset)




