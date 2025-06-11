

from repositories.enrollments import get_enrollment_by_id_repo
from data.models import EnrollmentResponse


async def get_enrollment_by_id(enrollment_id):
    enrollment = EnrollmentResponse(**await get_enrollment_by_id_repo(int(enrollment_id)))
    return enrollment