from typing import Callable, Any

from data.database import read_query

ALLOWED_ROLES = {
    "student": {
        "table": "v1.students",
        "fields": "email, first_name, last_name, avatar_url"
    },
    "teacher": {
        "table": "v1.teachers",
        "fields": "email, mobile, linked_in_url"
    },
}

async def get_account_by_email(
    email: str,
    role: str,
    get_data_func: Callable[[str, tuple], Any] = read_query
):
    role_info = ALLOWED_ROLES.get(role.lower())

    if not role_info:
        raise ValueError(f"Unsupported role: {role}")

    query = f"""
        SELECT {role_info['fields']}
        FROM {role_info['table']}
        WHERE email = %s
    """

    result = await get_data_func(query, (email,))
    return result[0] if result else None









