from common.responses import Unauthorized, Forbidden
from repositories.user_repo import get_account_by_email_repo, get_user_by_id_repo
from repositories.teacher_repo import (
    update_teacher_repo,
    report_enrolled_students_repo,
    deactivate_course_repo,
    verify_email_repo,
    validate_teacher_verified_and_activated_repo
)
from typing import Union
from data.models import UserRole, TeacherResponse
from repositories.user_repo import get_role_by_email_repo
from repositories.enrollments_repo import confirm_enrollment_repo

async def get_teacher_by_email(email):
    """
    Fetch a teacher's account information based on their email.

    This function queries the repository layer to retrieve account
    information with the specified role of 'teacher', corresponding
    to the provided email address. It is an asynchronous function
    designed to interact with the data source efficiently.

    :param email: The email address of the teacher whose account
        information is being retrieved.
    :type email: str
    :return: The account details of the teacher associated with the
        specified email, returned as the result of the repository query.
    :rtype: Any
    :raises ValueError: If invalid arguments are provided.
    :raises Exception: If there is an issue during data retrieval.
    """
    return await get_account_by_email_repo(email, role="teacher")

async def update_teacher_service(mobile, linked_in_url, email):
    """
    Update the teacher information in the repository and retrieve the updated teacher
    data by email.

    This function updates a teacher's details including mobile, LinkedIn URL, and email
    in the repository using `update_teacher_repo`. After updating, it fetches the updated
    data corresponding to the specified email using `get_teacher_by_email`.

    :param mobile: The updated mobile number of the teacher.
    :type mobile: str
    :param linked_in_url: The updated LinkedIn profile URL of the teacher.
    :type linked_in_url: str
    :param email: The email address of the teacher to fetch the updated record.
    :type email: str
    :return: The updated teacher information fetched from the repository.
    :rtype: Any
    """
    await update_teacher_repo(mobile, linked_in_url, email)
    return await get_teacher_by_email(email)

async def validate_teacher_role(email: str) -> Union[Unauthorized, Forbidden] | None:
    """
    Validates if the provided email corresponds to a User with a Teacher role. If the role
    is not Teacher, a `Forbidden` response object is returned. If the role is properly
    validated as Teacher, no value is returned (None).

    :param email: Email address of the user whose role is to be validated.
    :type email: str
    :return: A `Forbidden` response object if the email's role is not Teacher,
             otherwise returns None.
    :rtype: Union[Unauthorized, Forbidden] | None
    """
    role = await get_role_by_email_repo(email)
    if role != UserRole.TEACHER:
        return Forbidden(content="Only a Teacher user can perform this action")
    return None

async def get_enrolled_students(teacher_id: int):
    """
    Fetches a list of students enrolled under a specific teacher.

    This function queries the repository to retrieve the students
    enrolled with a teacher based on their unique identifier.

    :param teacher_id: The unique identifier of the teacher.
    :type teacher_id: int
    :return: A list of students enrolled under the teacher.
    :rtype: list
    """
    return await report_enrolled_students_repo(teacher_id)

async def deactivate_course_service(teacher_id: int, course_id: int):
    """
    Deactivates a course for a specific teacher by the given IDs. This function interacts
    with the repository layer to mark the course as deactivated or appropriately handle
    business logic for making the course inactive.

    :param teacher_id: The unique identifier of the teacher for whom the course will
                       be deactivated.
    :param course_id: The unique identifier of the course to be deactivated.
    :return: An awaitable result indicating the success or failure of the deactivate
             operation, as determined by the repository implementation.
    """
    return await deactivate_course_repo(teacher_id, course_id)

async def get_teacher_by_id(teacher_id: int):
    """
    Retrieve a teacher's information by their unique identifier.

    This function fetches the teacher's data based on the provided `teacher_id`
    from the repository. It then constructs a `TeacherResponse` object
    with the retrieved data.

    :param teacher_id: A unique identifier for the teacher.
    :type teacher_id: int
    :return: A `TeacherResponse` object containing the teacher's information.
    :rtype: TeacherResponse
    """
    teacher = await get_user_by_id_repo(teacher_id, role = "teacher")
    return TeacherResponse(**teacher)

async def confirm_enrollment(enrollment_id):
    """
    Confirm an enrollment using the provided enrollment ID.

    This function interacts with the repository layer to confirm the enrollment
    associated with the given enrollment ID asynchronously.

    :param enrollment_id: The unique identifier of the enrollment to be confirmed.
    :type enrollment_id: str
    :return: The confirmation status or result of the enrollment process.
    :rtype: Any
    """
    return await confirm_enrollment_repo(enrollment_id)

async def verify_email(teacher_id):
    """
    Verifies the email of a teacher by utilizing the corresponding repository logic.
    This function operates asynchronously.

    :param teacher_id: The unique identifier for the teacher whose email needs
        to be verified.
    :type teacher_id: str
    :return: The result of the email verification process, as provided by the
        repository function.
    :rtype: Any
    """
    return await verify_email_repo(teacher_id)

async def validate_teacher_verified_and_activated(teacher_id):
    """
    Validates whether a teacher is verified and activated based on the provided teacher ID.

    The function asynchronously checks if a teacher is marked as both
    verified and activated in the repository layer.

    :param teacher_id: The unique identifier of the teacher to validate.
    :type teacher_id: int
    :return: A boolean value indicating whether the teacher is both
        verified and activated.
    :rtype: bool
    """
    validation = await validate_teacher_verified_and_activated_repo(teacher_id)
    return True if validation else False