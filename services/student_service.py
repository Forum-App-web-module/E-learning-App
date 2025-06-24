from repositories.user_repo import get_account_by_email_repo, get_user_by_id_repo
from repositories.student_repo import (
    update_avatar_url_repo,
    update_student_data_repo,
    get_courses_student_all_repo,
    get_courses_progress_repo,
    rate_course_repo,
    allow_rating_repo, check_enrollment_repo
)
from data.models import StudentResponse
from repositories.section_repo import complete_section_repo, get_completed_sections_repo
from repositories.course_repo import complete_course_repo



async def update_student_service(first_name: str, last_name: str, avatar_url: str, user_email: str, user_role: str):
    """
    Updates the information of an existing student and retrieves the updated account details
    by email and role. This functionality is asynchronous, requiring non-blocking operations
    for database interaction and retrieval of user details.

    :param first_name: The first name of the student to be updated
    :param last_name: The last name of the student to be updated
    :param avatar_url: The URL of the student's avatar image
    :param user_email: The email address of the student
    :param user_role: The role of the user to fetch the updated account details
    :return: The updated account details corresponding to the given email and role
    """
    await update_student_data_repo(first_name, last_name, avatar_url, user_email)
    return await get_account_by_email_repo(user_email, user_role)

async def get_student_courses_service(student_id: int):
    """
    Retrieve all courses associated with a specific student based on their ID.

    This asynchronous function serves as a service layer method to interact with the repository for
    fetching all courses linked to the provided student ID. It acts as a bridge between the
    business logic and the underlying repository.

    :param student_id: The unique identifier of the student whose courses are to be retrieved.
    :type student_id: int
    :return: A list of courses associated with the given student ID.
    :rtype: List[Any]
    """
    return await get_courses_student_all_repo(student_id)

async def get_student_courses_progress_service(student_id: int):
    """
    Fetches the progress of courses for a specific student by their ID.

    This asynchronous function retrieves the course progress information for
    the student identified by the provided student ID. The function interacts
    with the underlying repository layer to query the necessary progress data.

    :param student_id: The unique identifier of the student whose course
        progress is to be retrieved.
    :type student_id: int
    :return: A coroutine that resolves to the course progress data for the
        specified student.
    :rtype: Any
    """
    return await get_courses_progress_repo(student_id)

async def update_avatar_url(url: str, user_email):
    return await update_avatar_url_repo(url, user_email)


async def get_student_by_email(email):
    """
    Retrieve a student account based on the provided email address.

    This function fetches the details of a student account by email. It
    utilizes the repository function `get_account_by_email_repo` to retrieve
    the specific account associated with the given email address. The role
    for this search is specified as "student".

    :param email: The email address associated with the student account.
    :type email: str
    :return: The account details of the student associated with the provided email.
    :rtype: Any
    """
    return await get_account_by_email_repo(email, role="student")

async def rate_course_service(student_id: int, course_id: int, rating: int):
    """
    Asynchronous function to rate a course. This function first checks whether the student
    is allowed to rate the given course by invoking a repository, and if allowed, it
    proceeds to record the provided rating for the course.

    :param student_id: The unique identifier of the student attempting to rate the course
    :param course_id: The unique identifier of the course being rated
    :param rating: The rating score the student assigns to the course
    :return: Returns the result of the course rating operation, which depends on the
             repository implementation. It may return None if the student is not allowed
             to rate the course.

    """
    is_allowed = await allow_rating_repo(student_id, course_id)
    if not is_allowed:
        return None
    
    return await rate_course_repo(student_id, course_id, rating)

async def get_student_by_id(student_id: int):
    """
    Retrieve a student's information by their unique ID asynchronously.

    This function interacts with the repository layer to fetch user details
    for a specific student based on their ID. It then transforms and returns
    the data in the form of a serialized student response.

    :param student_id: The unique identifier of the student to be retrieved.
    :type student_id: int

    :return: The serialized JSON representation of the student's information.
    :rtype: Dict
    """
    student = await get_user_by_id_repo(student_id, role = "student")
    return StudentResponse(**student).model_dump(mode="json")


async def complete_section_service(student_id: int, section_id: int):
    """
    Complete a specific section for a given student.

    This function interacts with the repository layer to mark a specific section
    as completed for a particular student. It takes both the student identifier
    and the section identifier as inputs and completes the corresponding
    operation asynchronously.

    :param student_id: The unique identifier of the student.
    :type student_id: int
    :param section_id: The unique identifier of the section to be completed.
    :type section_id: int
    :return: The result of the repository operation for completing the section.
    :rtype: Any
    """
    return await complete_section_repo(student_id, section_id)

async def complete_course_service(student_id: int, course_id: int):
    """
    Complete the course for a given student by interacting with the repository layer.

    This function is part of the service layer that takes a student's ID and a course ID
    as input and interacts with the repository to mark the course as completed for the
    student. It ensures that the service logic is separated from the data layer, maintaining
    a clean architecture.

    :param student_id: The unique identifier of the student.
    :type student_id: int
    :param course_id: The unique identifier of the course to be completed.
    :type course_id: int
    :return: The result of the repository operation for completing the course.
    :rtype: The return type depends on the implementation of `complete_course_repo`.
    """
    return await complete_course_repo(student_id, course_id)

async def get_completed_sections_service(course_id: int, student_id: int):
    """
    Fetch the completed sections for a student in a given course asynchronously.

    This function interacts with the repository layer to retrieve the sections
    that a specific student has completed in a specific course. The actual
    data-fetching operation is delegated to the `get_completed_sections_repo`
    function.

    :param course_id: The unique identifier representing the course.
    :type course_id: int
    :param student_id: The unique identifier representing the student.
    :type student_id: int
    :return: A list of sections that the student has completed in the course.
    :rtype: Awaitable
    """
    return await get_completed_sections_repo(course_id, student_id)

async def check_enrollment_service(course_id: int, student_id: int):
    """
    Checks if a student is enrolled in a specific course.

    The function verifies the enrollment of a student in a given course by
    communicating with the repository layer. It takes the course ID and
    student ID as inputs and returns the enrollment status.

    :param course_id: The unique identifier for the course to check.
    :param student_id: The unique identifier for the student whose enrollment
                       status needs to be verified.
    :return: A boolean indicating whether the student is enrolled in the
             specified course or not.
    """
    return await check_enrollment_repo(course_id, student_id)