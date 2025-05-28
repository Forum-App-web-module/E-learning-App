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
        role_query = "INSERT INTO v1.students (email, password) VALUES (%s, %s) RETURNING id"
        id = insert_data_func(role_query, (data.email, hashed_password))
    elif isinstance(data, TeacherRegisterData):
        role = UserRole.TEACHER
        role_query = "INSERT INTO v1.teachers (email, password, mobile, linked_in_url) VALUES (%s, %s, %s, %s) RETURNING id"
        id = insert_data_func(role_query, (data.email, hashed_password ,data.mobile, data.linked_in_url))

    return role, id

# checks if an email exists, to be used when registring
def email_exists(email: str, get_data_func = read_query):

    query = """SELECT email FROM v1.students UNION SELECT email from v1.teachers WHERE email = %s"""
    result = get_data_func(query, (email,))
    return bool(result)


# deactivates user, admin rights needed
def deactivate_user(email: str, role: UserRole, update_data_func = update_query):

    query = f"""
    UPDATE v1.{role}
    SET is_active = FALSE
    WHERE email = %s
    """
    result = update_data_func(query, (email, ))
    return result

def get_hash_by_email(email: str, get_data_func = read_query):
    query = "SELECT password FROM v1.students WHERE email = %s" \
    "UNION " \
    "SELECT password FROM v1.teachers WHERE email = %s" \
    "UNION" \
    "SELECT password FROM v1.admins WHERE email = %s"

    return get_data_func(query, (email, email, email))[0][0]

# to avoid code repetition
# check if the user role is the same as the required one
def check_user_role(token: str, role: UserRole):
    user = verify_access_token(token)
    if user.get("role") != role:
        raise Forbidden
    return True
