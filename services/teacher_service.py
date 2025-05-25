from data.database import read_query, insert_query, update_query
from services.user_service import create_user, find_user_by_email
from data.models import Teacher, TeacherRegisterData, UserRole

# registers a new teacher, using create_user from user service should also add an entry in the users table 
def register_teacher(data: TeacherRegisterData, avatar_url: str = None, insert_data_func = None): #TODO check both tables
    if insert_data_func is None:
        insert_data_func = insert_query

    create_user(data=data, role=UserRole.TEACHER, avatar_url=avatar_url)

    user = find_user_by_email(data.email)
    if not user:
        return None
    
    user_id = user["id"]

    query = """
        INSERT INTO teachers (user_id, mobile, linked_in_url, email_verified)
        VALUES (%s, %s ,%s , FALSE)
    """
    new_teacher = insert_data_func(query, (user_id, data.mobile, data.linked_in_url))
    return new_teacher

def get_teacher_by_id():
    pass

def get_teacher_by_email():
    pass

def verify_teacher_email():
    pass