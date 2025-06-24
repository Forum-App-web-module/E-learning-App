from repositories.enrollments_repo import (
    get_enrollment_by_id_repo,
    get_enrollment_by_student_course_repo,
    unenroll_student_repo)
from repositories.student_repo import get_courses_progress_repo
from data.models import EnrollmentResponse


async def get_enrollment_by_id(enrollment_id):
    """
    Fetches the enrollment details for a given enrollment ID.

    This asynchronous function retrieves the enrollment data
    associated with the provided enrollment ID by querying
    the data repository. If the enrollment record is found,
    it constructs and returns an instance of `EnrollmentResponse`.
    Returns `None` if no matching enrollment is found.

    :param enrollment_id: The ID of the enrollment to retrieve.
    :type enrollment_id: int
    :return: An instance of `EnrollmentResponse` containing the
        enrollment details, or `None` if no enrollment is found.
    :rtype: EnrollmentResponse or None
    """
    enrollment = await get_enrollment_by_id_repo(int(enrollment_id))
    if enrollment:
        enrollment_response = EnrollmentResponse(**enrollment)
        return enrollment_response
    return None

async def unenroll_student_service(student_id: int, course_id: int):
    """
    This service function handles the unenrollment of a student from a specific course. It checks the
    student's progress in the course before confirming whether the unenrollment should be marked as
    a dropout. If an enrollment record exists for the given student and course, the system processes
    the unenrollment; otherwise, it returns None.

    :param student_id: The unique identifier of the student to be unenrolled
    :param course_id: The unique identifier of the course from which the student is to be unenrolled
    :return: A result from the unenrollment repository, if enrollment exists; otherwise, None
    """
    progress_response = await get_courses_progress_repo(student_id)
    filtered_response = list(filter(lambda x: x["course_id"] == course_id, progress_response))
    drop_out = filtered_response[0]["progress_percentage"] < 100
    enrollment_response = await get_enrollment_by_student_course_repo(student_id, course_id)

    if enrollment_response:
        return await unenroll_student_repo(enrollment_response["id"], drop_out)
    else:
        return None











