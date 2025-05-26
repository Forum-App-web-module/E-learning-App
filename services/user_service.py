from data.database import read_query, insert_query, update_query
from security.secrets import hash_password
from data.models import RegisterData, UserRole, StudentRegisterData, TeacherRegisterData
from security.jwt_auth import verify_access_token
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from common.responses import Unauthorized, Forbidden

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_account(data, hashed_password, insert_data_func = insert_query):
    if isinstance(data, StudentRegisterData):
        role = UserRole.STUDENT
    elif isinstance(data, TeacherRegisterData):
        role = UserRole.TEACHER

    users_query = "INSERT INTO v1.users (role, email, first_name, last_name, password) VALUES (%s, %s, %s, %s, %s) RETURNING id"
    user_id = insert_data_func(users_query, (role, data.email, data.first_name, data.last_name, hashed_password))

    if role == UserRole.STUDENT:
        role_query = "INSERT INTO v1.students (user_id) VALUES (%s) RETURNING id"
        id = insert_data_func(role_query, (user_id,))
    elif role == UserRole.TEACHER:
        role_query = "INSERT INTO v1.teachers (user_id, mobile, linked_in_url) VALUES (%s, %s, %s) RETURNING id"
        id = insert_data_func(role_query, (user_id, data.mobile, data.linked_in_url))

    return role, id



#lists all users, maybe admin rights needed
def get_users():
    query = '''
        SELECT id, email, first_name, last_name, role, is_active, created_on
        FROM v1.users
        ORDER BY created_on DESC
    '''
    return read_query(query)

# find user by email, admin rights needed
def find_user_by_email(email: str, get_data_func = None):
    if get_data_func is None:
        get_data_func = read_query

    query = """
        SELECT id, email, first_name, last_name, role, avatar_url, is_active, notifications, created_on
        FROM v1.users
        WHERE email = %s
    """
    result = get_data_func(query, (email,))
    row = result[0] if result else None
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "role": row[4],
            "avatar_url": row[5],
            "is_active": row[6],
            "notifications": row[7],
            "created_on": row[8]
        }
    return None

# checks if an email exists, to be used when registring
def email_exists(email: str, get_data_func = None):
    if get_data_func is None:
        get_data_func = read_query

    query = """SELECT 1 FROM v1.users WHERE email = %s"""
    result = get_data_func(query, (email,))
    return bool(result)

# deactivates a user, admin rights needed
def deactivate_ser(user_id: int, update_data_func = None):
    if update_data_func is None:
        update_data_func = update_query
    query = """
    UPDATE v1.users
    SET is_active = FALSE
    WHERE id = %s
    """
    result = update_data_func(query, (user_id, ))
    return result

def get_hash_by_email(email: str, get_data_func = read_query):
    query = "SELECT password FROM v1.users WHERE email = %s"
    return get_data_func(query, (email,))[0][0]

def is_student(token:str):
    user = get_current_user(token)          #return check_user_role(token, "student")
    if user.get("role") != "student":
        raise Forbidden
    return True

def is_teacher(token:str):
    user = get_current_user(token)          #return check_user_role(token, "teacher")
    if user.get("role") != "teacher":
        raise Forbidden
    return True

def is_admin(token:str):
    user = get_current_user(token)          #return check_user_role(token, "admin")
    if user.get("role") != "admin":
        raise Forbidden
    return True

def get_current_user(token:str):
    try:
        user = verify_access_token(token)
        return user
    except Exception:
        raise Unauthorized

# to avoid code repetition
# check if the user role is the same as the required one
def check_user_role(token: str, role: str):
    user = verify_access_token(token)
    if user.get("role") != role:
        raise Forbidden
    return True
