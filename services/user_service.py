from data.database import read_query, insert_query, update_query
from security.secrets import hash_password
from data.models import RegisterData, UserRole


def create_user(data:RegisterData, role: UserRole, avatar_url: str = None, insert_func=None):
    if insert_func is None:
        insert_func = insert_query

    hashed_pw = hash_password(data.password)
    query = """
        INSERT into users (email, first_name, last_name, password, role, avatar_url, is_active, notifications, created_on)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE, TRUE, NOW())"""
    
    new_user = insert_func(query, (
        data.email,
        data.first_name,
        data.last_name,
        hashed_pw,
        role.value,
        avatar_url
    ))
    return new_user

#lists all users, maybe admin rights needed
def get_users():
    query = '''
        SELECT id, email, first_name, last_name, role, is_active, created_on
        FROM users
        ORDER BY created_on DESC
    '''
    return read_query(query)

# find user by email, admin rights needed
def find_user_by_email(email: str, get_data_func = None):
    if get_data_func is None:
        get_data_func = read_query

    query = """
        SELECT id, email, first_name, last_name, role, avatar_url, is_active, notifications, created_on
        FROM users
        WHERE email = ?
    """
    result = get_data_func(query, (email,))
    return result[0] if result else None

# checks if an email exists, to be used when registring
def email_exists(email: str, get_data_func = None):
    if get_data_func is None:
        get_data_func = read_query

    query = """SELECT 1 FROM users WHERE email = ?"""
    result = get_data_func(query, (email,))
    return bool(result)

# deactivates a user, admin rights needed
def deactivate_ser(user_id: int, update_data_func = None):
    if update_data_func is None:
        update_data_func = update_query
    query = """
    UPDATE users
    SET is_active = FALSE
    WHERE id = ?
    """
    result = update_data_func(query, (user_id, ))
    return result