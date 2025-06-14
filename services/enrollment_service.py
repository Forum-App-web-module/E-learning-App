from repositories.enrollments_repo import (
    get_enrollment_by_id_repo,
    get_enrollment_by_student_course_repo,
    unenroll_student_repo)
from repositories.student_repo import repo_get_courses_progress
from data.models import EnrollmentResponse


async def get_enrollment_by_id(enrollment_id):
    enrollment = EnrollmentResponse(**await get_enrollment_by_id_repo(int(enrollment_id)))
    return enrollment

async def unenroll_student_service(student_id: int, course_id: int):
    progress_response = await repo_get_courses_progress(student_id)
    filtered_response = list(filter(lambda x: x["course_id"] == course_id, progress_response))
    drop_out = filtered_response[0]["progress_percentage"] < 100
    enrollment_response = await get_enrollment_by_student_course_repo(student_id, course_id)

    if enrollment_response:
        return await unenroll_student_repo(enrollment_response["id"], drop_out)
    else:
        return None











