
from data.database import update_query
from data.models import Action_UserRole, Action


async def change_account_state_repo(role: Action_UserRole, action: Action, user_id: id, update_date_func = update_query) -> int | None:
    """
    :param role: Action_UserRole.student | Action_UserRole.teacher | Action_UserRole.admin
    :param action: Action.deactivate | Action.activate
    :param user_id: int
    :param update_date_func: None | mock_update_query
    :return updated row count: int | None
    """
    
    query = f"""UPDATE v1.{role.value}s SET is_active = $1 WHERE id = $2"""

    if action == Action.deactivate:
        action_bool = False
    elif action == Action.activate:
        action_bool = True

    update = await update_date_func(query,(action_bool, user_id))
    return update


async def soft_delete_course_repo(course_id, update_date_func = update_query) -> int | None:
    """
    :param course_id: int
    :param update_date_func: None | mock_update_query
    :return int | None: returns updated row count
    """
    query = """
        UPDATE v1.courses SET is_hidden = $1 WHERE id = $2
    """
    hidden_rows = await update_date_func(query, (True ,course_id))

    return hidden_rows
