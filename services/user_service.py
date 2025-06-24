from pydantic import EmailStr
from data.database import read_query, update_query
from data.models import UserRole, StudentRegisterData, TeacherRegisterData
from fastapi.security import OAuth2PasswordBearer
from repositories.user_repo import insert_user_repo, email_exists_repo, get_role_by_email_repo
from typing import Union


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def create_account(data: Union[TeacherRegisterData, StudentRegisterData], hashed_password: str):
    """
    Creates an account for a user based on the provided registration data and hashed password.
    This function determines the user's role and inserts their data into the repository.

    :param data: The registration information for the user. It can either be an instance
        of TeacherRegisterData or StudentRegisterData.
    :param hashed_password: The hashed version of the user's password.
    :return: A tuple consisting of the user's role and the user ID.
    """
    role, user_id = await insert_user_repo(data, hashed_password)
    return role, user_id

# call repo layer email_exists
async def email_exists(email: EmailStr) -> bool:
    """
    Checks if the given email address exists in storage.

    This function is an abstraction over the repository layer that queries
    whether a specific email address is present in the database or any other
    persistent storage. It accepts an email address as input and returns a
    boolean value indicating its existence.

    :param email: The email address to be verified for existence.
    :type email: EmailStr
    :return: True if the email exists; False otherwise.
    :rtype: bool
    """
    return await email_exists_repo(email)

async def get_hash_by_email(email: EmailStr, get_data_func = read_query):
    """
    Fetches the hashed password associated with an email from different tables in the database.
    The function performs an asynchronous SQL query to retrieve the hashed password
    from one of the tables (`v1.students`, `v1.teachers`, or `v1.admins`) corresponding
    to the specified email address. It uses a passed data retrieval function to execute
    the query.

    :param email: The email address for which the hashed password is being requested.
    :type email: EmailStr
    :param get_data_func: Asynchronous function for retrieving data from the database.
        Defaults to `read_query` if no function is passed.
    :return: The hashed password associated with the provided email.
    :rtype: str
    """
    query = """
        SELECT password FROM v1.students WHERE email = $1
        UNION
        SELECT password FROM v1.teachers WHERE email = $2
        UNION
        SELECT password FROM v1.admins WHERE email = $3
    """

    result = await get_data_func(query, (email, email, email))

    return result[0][0]

async def get_role_by_email(email):
    return await get_role_by_email_repo(email)
