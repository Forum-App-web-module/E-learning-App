from repositories.section_repo import insert_section_repo, update_section_repo, get_all_course_sections_repo, hide_section_repo
from repositories.student_repo import check_enrollment_repo, validate_subscription_repo
from data.models import SectionCreate, SectionUpdate
from repositories.course_repo import get_course_by_id_repo

async def create_section_service(course_id: int, section: SectionCreate):
    """
    Creates a new section for the specified course.

    This function serves as a service layer to handle the creation
    of a new section for a given course. It communicates with the
    repository to persist the section data.

    :param course_id: The unique identifier of the course for which
        the section is to be created.
    :param section: The details of the section to be created, encapsulated
        in a `SectionCreate` object.
    :return: The result of the section insertion operation, as provided
        by the repository.
    """
    return await insert_section_repo(course_id, section)
    
async def get_all_sections_per_course_service(course_id, sort_by: str = "id", order: str = "asc"):
    """
    Fetches all sections for a given course from the repository using specified sorting
    criteria.

    This asynchronous function retrieves course sections, optionally sorted by a specific
    field in ascending or descending order. The data is fetched from the repository layer.

    :param course_id: Unique identifier for the course for which sections are fetched.
    :type course_id: int
    :param sort_by: Field by which to sort the sections. Defaults to "id".
    :type sort_by: str
    :param order: Sorting order, either "asc" for ascending or "desc" for descending.
        Defaults to "asc".
    :type order: str
    :return: A list of course sections corresponding to the given course id, sorted as
        specified.
    :rtype: list
    """
    return await get_all_course_sections_repo(course_id, sort_by, order)

async def update_section_service(course_id: int, updates: SectionUpdate):
    """
    Updates a section in the repository with the provided course ID and updates.

    This function facilitates the process of asynchronously updating a
    specific section within a course by delegating the task to the underlying
    repository function.

    :param course_id: The unique identifier of the course containing the section
        to be updated.
    :type course_id: int
    :param updates: An object encapsulating the updates to be applied to the
        section.
    :type updates: SectionUpdate
    :return: A coroutine resolving to the updated section data or resulting
        success/failure state, as defined by the repository function.
    :rtype: Any
    """
    return await update_section_repo(course_id, updates)

async def hide_section_service(section_id: int):
    """
    Hides a specific section identified by its ID.

    This asynchronous function interacts with the repository layer to execute the
    logic for hiding a section in the system.

    :param section_id: An integer representing the unique ID of the section to be hidden.
    :return: A coroutine that performs the section hiding operation.
    """
    return await hide_section_repo(section_id)
    
async def is_student_allowed_to_view_sections(course_id: int, student_id: int):
    """
    Determines if a student is allowed to view sections of a course.

    This function checks whether a student is enrolled in the specified course and whether
    the course is premium. If the course is premium, it validates that the student has an
    active subscription allowing access to premium courses.

    :param course_id: The unique identifier of the course the student wants to view.
    :type course_id: int
    :param student_id: The unique identifier of the student attempting to access the course.
    :type student_id: int
    :return: A boolean indicating whether the student is allowed to view sections of the course.
    :rtype: bool
    """
    enrolled = await check_enrollment_repo(course_id, student_id)
    if not enrolled:
        return False
    course = await get_course_by_id_repo(course_id)
    if not course:
        return False 

    if course["is_premium"]:
        return await validate_subscription_repo(student_id)
    
    return True 