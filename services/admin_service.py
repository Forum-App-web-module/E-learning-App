from repositories.admin_repo import change_account_state_repo, soft_delete_course_repo
from repositories.teacher_repo import report_enrolled_students_repo
from repositories.course_repo import get_course_by_id_repo, admin_course_view_repo
from repositories.enrollments_repo import unenroll_all_by_course_id_repo
from data.models import Action_UserRole, Action

async def change_account_state(role: Action_UserRole, action: Action, user_id: int) -> int | None:
    """
    :param role: Action_UserRole.student | Action_UserRole.teacher | Action_UserRole.admin
    :param action: Action.deactivate | Action.activate
    :param user_id: int
    :return updated row count: int | None
    """
    change = await change_account_state_repo(role, action, user_id)
    return change if change else None


async def soft_delete_course_service(course_id: int) -> tuple[list[str], int] | tuple[None, None]:
    """
    :param course_id:
    :return tuple[list[str], int] | tuple[None, None]:
    """
    course_data = await get_course_by_id_repo(course_id)
    if course_data:
        owner_id = course_data["owner_id"]
        enrolled_students_data = await report_enrolled_students_repo(owner_id)

        soft_deleted_row_count = await soft_delete_course_repo(course_id)
        if soft_deleted_row_count:
            await unenroll_all_by_course_id_repo(course_id)
        
        student_emails = [row["email"] for row in enrolled_students_data]
        
        return student_emails, soft_deleted_row_count
    else:
        return None, None

async def get_admin_courses_view_service(
        title: str = "",
        teacher_id: int = None,
        student_id: int = None,
        limit: int = 5,
        offset: int = 0):
    """

    :param title: "" | course title to filter by.
    :param teacher_id: None | teacher_id to filter by.
    :param student_id: None | student_id to filter by.
    :param limit: 5 | limit of rows to return.
    :param offset: 0 | offset of rows to return.
    :return: Record(
        id,
        title,
        is_premium,
        description,
        tags,
        picture_url,
        owner_id,
        created_on,
        students_count,
        average_rating)
    """
    return await admin_course_view_repo(title, teacher_id, student_id, limit, offset)




