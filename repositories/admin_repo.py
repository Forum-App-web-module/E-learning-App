
from data.database import update_query
from data.models import Action_UserRole, Action


async def change_account_state_repo(role: Action_UserRole, action: Action, user_id: id, update_date_func = update_query):
    
    query = f"UPDATE v1.{role.value}s SET is_active = $1 WHERE id = $2"

    if action == Action.deactivate:
        action_bool = False
    elif action == Action.activate:
        action_bool = True

    update = await update_date_func(query,(action_bool, user_id))
    return update


async def delete_course_repo(course_id, update_date_func = update_query):
    query = """
        DELETE FROM v1.courses 
        WHERE id = $1;
    """
    deleted_rows = await update_date_func(query, (course_id, ))

    return deleted_rows
