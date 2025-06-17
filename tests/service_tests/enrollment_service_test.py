import pytest
from unittest.mock import patch, AsyncMock
from services.enrollment_service import (
    get_enrollment_by_id,
    EnrollmentResponse,
    unenroll_student_service
)

@pytest.mark.asyncio
class TestGetEnrollmentByIdShould:
    async def test_found(self):
        fake_data = {
            "id": 1,
            "student_id": 23,
            "course_id": 123,
            "is_approved": True,
            "requested_at": "2025-01-01",
            "approved_at": "2025-01-02",
            "completed_at": "2025-01-03",
            "drop_out": False
        }

        with patch("services.enrollment_service.get_enrollment_by_id_repo", new_callable=AsyncMock) as mock_repo:
            mock_repo.return_value = fake_data

            result = await get_enrollment_by_id(1)

            assert isinstance(result, EnrollmentResponse)
            mock_repo.assert_awaited_once_with(1)

    async def test_not_found(self):
        with patch("services.enrollment_service.get_enrollment_by_id_repo", new_callable=AsyncMock) as mock_repo:
            mock_repo.return_value = None

            result = await get_enrollment_by_id(1)

            assert result is None
            mock_repo.assert_awaited_once_with(1)

@pytest.mark.asyncio
class TestUnenrollStudentShould:

    async def test_unenrolls_if_enrollment_found(self):
        student_id = 1
        course_id = 101

        # Fake stuff
        fake_progress = [{"course_id": course_id, "progress_percentage": 15}]
        fake_enrollment = {"id": 2}
        fake_unenroll_result = {"status": "success"}

        with patch(
            "services.enrollment_service.get_courses_progress_repo",
            new_callable=AsyncMock
        ) as mock_get_progress, \
             patch(
                 "services.enrollment_service.get_enrollment_by_student_course_repo",
                 new_callable=AsyncMock
             ) as mock_get_enrollment, \
             patch(
                 "services.enrollment_service.unenroll_student_repo",
                 new_callable=AsyncMock
             ) as mock_unenroll_repo:

            mock_get_progress.return_value = fake_progress
            mock_get_enrollment.return_value = fake_enrollment
            mock_unenroll_repo.return_value = fake_unenroll_result

            result = await unenroll_student_service(student_id, course_id)

            assert result == fake_unenroll_result
            mock_get_progress.assert_awaited_once_with(student_id)
            mock_get_enrollment.assert_awaited_once_with(student_id, course_id)
            mock_unenroll_repo.assert_awaited_once_with(2, True)  # dropout = True (75% < 100)

    async def test_returns_none_if_enrollment_not_found(self):
        student_id = 2
        course_id = 22

        fake_progress = [{"course_id": course_id, "progress_percentage": 100}]

        with patch(
            "services.enrollment_service.get_courses_progress_repo",
            new_callable=AsyncMock
        ) as mock_get_progress, \
             patch(
                 "services.enrollment_service.get_enrollment_by_student_course_repo",
                 new_callable=AsyncMock
             ) as mock_get_enrollment, \
             patch(
                 "services.enrollment_service.unenroll_student_repo",
                 new_callable=AsyncMock
             ) as mock_unenroll_repo:

            mock_get_progress.return_value = fake_progress
            mock_get_enrollment.return_value = None  # mock no enrollment

            result = await unenroll_student_service(student_id, course_id)

            assert result is None
            mock_get_progress.assert_awaited_once_with(student_id)
            mock_get_enrollment.assert_awaited_once_with(student_id, course_id)
            mock_unenroll_repo.assert_not_awaited()
