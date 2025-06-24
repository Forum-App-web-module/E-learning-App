from repositories.course_repo import (
    get_all_courses_per_teacher_repo, get_course_by_id_repo, insert_course_repo, update_course_data_repo, get_all_courses_repo,
    get_all_student_courses_repo, count_premium_enrollments_repo, get_course_rating_repo)
from repositories.student_repo import validate_subscription_repo
from data.models import CourseCreate, CourseUpdate, CourseFilterOptions, StudentCourseFilter, TeacherCourseFilter
from asyncpg.exceptions import UniqueViolationError
from fastapi.exceptions import HTTPException
from repositories.enrollments_repo import create_enrollment_repo
from typing import Optional

async def get_all_courses_service(filters: CourseFilterOptions, student_id: Optional[int] = None):
    """
    Fetches all courses based on the given filter options and an optional student ID for premium validation.

    This function retrieves courses based on specific filter criteria. If a student ID is
    provided, it verifies whether the student has a premium subscription. The premium
    status will affect the list of courses returned.

    :param filters: The filter criteria for the course selection.
    :type filters: CourseFilterOptions
    :param student_id: Optional ID of the student to check for premium subscription status.
                       Defaults to None.
    :type student_id: Optional[int]

    :return: A list of courses based on the provided filters and subscription status.
    :rtype: List[Course]
    """
    premium = False
    if student_id:
        premium = await validate_subscription_repo(student_id)
    return await get_all_courses_repo(filters, premium)

async def get_course_by_id_service(id: int):
    """
    Fetches a course by its unique identifier asynchronously.

    This function communicates with the repository layer to retrieve the course
    details associated with the provided `id`. It serves as a service layer method,
    facilitating separation of concerns between business logic and data access.

    :param id: The unique identifier of the course to fetch.
    :type id: int
    :return: The course object corresponding to the given `id`, as returned by
        the repository layer.
    :rtype: Any
    """
    return await get_course_by_id_repo(id)

async def get_all_courses_per_teacher_service(teacher_id, filters: TeacherCourseFilter):
    """
    Retrieve all courses associated with a specific teacher, applying any associated filters,
    and returning the data from the repository layer asynchronously.

    :param teacher_id: The identifier of the teacher whose courses need to be retrieved.
    :type teacher_id: int
    :param filters: Object containing filtering criteria for querying the teacher's courses.
    :type filters: TeacherCourseFilter
    :return: A list of courses matching the specified teacher ID and any applied filters.
    :rtype: list
    """
    return await get_all_courses_per_teacher_repo(teacher_id, filters)

async def get_all_courses_per_student_service(student_id, filters: StudentCourseFilter):
    """
    Retrieve all courses associated with a student based on the given filters.

    This function interacts with a repository to fetch the course data related
    to a specific student. The filters allow flexibility in narrowing down the
    query results based on specific criteria.

    :param student_id: The unique identifier for the student.
    :type student_id: int
    :param filters: The filtering criteria to refine the course search.
    :type filters: StudentCourseFilter
    :return: A collection of courses associated with the specified student,
             potentially filtered based on the provided filters.
    :rtype: Any
    """
    return await get_all_student_courses_repo(student_id, filters)

async def create_course_service(course_data: CourseCreate):
    """
    Creates a new course in the system using the provided course data. This method interacts
    with the database to persist the course details. In case a course with the same title
    already exists, an exception is raised.

    :param course_data: The data required to create a new course, including its title
        and other relevant attributes.
    :type course_data: CourseCreate
    :return: The created course record upon successful insertion.
    :rtype: Depends on the return type of `insert_course_repo`.
    :raises HTTPException: If a course with the same title already exists, an HTTPException
        with a 400 status code and a relevant error message is raised.
    """
    try:
        return await insert_course_repo(course_data)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="Course with this title already exists")

async def update_course_service(id: int, updates: CourseUpdate):
    """
    Updates a course by its identifier with the provided data. This function interacts
    with the data repository to perform the update operation asynchronously.

    :param id: The unique identifier of the course to be updated.
    :param updates: An instance of CourseUpdate containing the new data for the course.
    :return: A coroutine that resolves once the update operation is complete.
    """
    return await update_course_data_repo(id, updates)


async def enroll_course(course_id: int, student_id: int):
    """
    Handle the enrollment of a student in a course asynchronously. The function takes
    the course ID and student ID as inputs, processes the enrollment through a
    repository function, and returns the unique enrollment ID.

    :param course_id: Unique identifier for the course.
    :type course_id: int
    :param student_id: Unique identifier for the student.
    :type student_id: int
    :return: The unique identifier for the enrollment.
    :rtype: int
    """
    enrollment_id = await create_enrollment_repo(course_id, student_id)
    return enrollment_id


async def count_premium_enrollments(student_id):
    """
    Counts the number of premium enrollments for a given student asynchronously.

    This function communicates with the associated repository layer to retrieve
    the count of premium enrollments for the specified student ID.

    :param student_id: The unique identifier of the student for whom the premium
        enrollments are to be counted.
    :type student_id: int
    :return: The total count of premium enrollments for the provided student ID.
    :rtype: int
    """
    return await count_premium_enrollments_repo(student_id)

async def get_course_rating_service(course_id: int):
    """
    Fetches the rating details of a specific course from the repository.

    This asynchronous method retrieves course ratings using the provided course
    identifier. The function interacts with the repository level to fetch
    data and transforms it into a list of dictionaries for easier handling.

    :param course_id: Unique identifier of the course whose ratings need to be
                      fetched.
    :type course_id: int
    :return: List of dictionaries containing the course rating information.
    :rtype: List[Dict]
    """
    data = await get_course_rating_repo(course_id) 
    return [dict(row) for row in data] 