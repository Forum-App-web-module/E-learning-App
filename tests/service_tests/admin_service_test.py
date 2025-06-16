import pytest
from unittest.mock import AsyncMock, patch
from services.admin_service import soft_delete_course_service


@pytest.mark.asyncio
class TestSoftDeleteCourseService:
    async def test_soft_delete_course_success_and_unenrolls(self):
        # Arrange
        course_id = 13
        fake_course_data = {"owner_id": 3}
        fake_students = [{"email": "moodle@example.com"}, {"email": "poodle@example.com"}]
        soft_deleted_count = 1

        # Act and Assert
        with patch("services.admin_service.get_course_by_id_repo", new_callable=AsyncMock) as mock_get_course, \
            patch("services.admin_service.report_enrolled_students_repo",
                  new_callable=AsyncMock) as mock_report_students, \
            patch("services.admin_service.soft_delete_course_repo", new_callable=AsyncMock) as mock_soft_delete, \
            patch("services.admin_service.unenroll_all_by_course_id_repo",
                  new_callable=AsyncMock) as mock_unenroll_all:

            mock_get_course.return_value = fake_course_data
            mock_report_students.return_value = fake_students
            mock_soft_delete.return_value = soft_deleted_count

            emails, row_count = await soft_delete_course_service(course_id)

            assert emails == ["moodle@example.com", "poodle@example.com"]
            assert row_count == soft_deleted_count

            mock_get_course.assert_awaited_once_with(course_id)
            mock_report_students.assert_awaited_once_with(fake_course_data["owner_id"])
            mock_soft_delete.assert_awaited_once_with(course_id)
            mock_unenroll_all.assert_awaited_once_with(course_id)

    async def test_soft_delete_course_success_but_no_rows_deleted(self):
        # Arrange
        course_id = 1
        fake_course_data = {"owner_id": 3}
        fake_students = [{"email": "moodle@example.com"}]
        soft_deleted_count = 0

        # Act and Assert
        with patch("services.admin_service.get_course_by_id_repo", new_callable=AsyncMock) as mock_get_course, \
                patch("services.admin_service.report_enrolled_students_repo",
                      new_callable=AsyncMock) as mock_report_students, \
                patch("services.admin_service.soft_delete_course_repo", new_callable=AsyncMock) as mock_soft_delete, \
                patch("services.admin_service.unenroll_all_by_course_id_repo",
                      new_callable=AsyncMock) as mock_unenroll_all:

            mock_get_course.return_value = fake_course_data
            mock_report_students.return_value = fake_students
            mock_soft_delete.return_value = soft_deleted_count

            emails, row_count = await soft_delete_course_service(course_id)

            assert emails == ["moodle@example.com"]
            assert row_count == 0

            mock_get_course.assert_awaited_once_with(course_id)
            mock_report_students.assert_awaited_once_with(fake_course_data["owner_id"])
            mock_soft_delete.assert_awaited_once_with(course_id)
            mock_unenroll_all.assert_not_awaited()

    async def test_soft_delete_course_not_found(self):
        # Arrange
        course_id = 1

        # Act and Assert
        with patch("services.admin_service.get_course_by_id_repo", new_callable=AsyncMock) as mock_get_course, \
                patch("services.admin_service.report_enrolled_students_repo",
                      new_callable=AsyncMock) as mock_report_students, \
                patch("services.admin_service.soft_delete_course_repo", new_callable=AsyncMock) as mock_soft_delete, \
                patch("services.admin_service.unenroll_all_by_course_id_repo",
                      new_callable=AsyncMock) as mock_unenroll_all:

            mock_get_course.return_value = None

            emails, row_count = await soft_delete_course_service(course_id)

            assert emails is None
            assert row_count is None

            mock_get_course.assert_awaited_once_with(course_id)
            mock_report_students.assert_not_awaited()
            mock_soft_delete.assert_not_awaited()
            mock_unenroll_all.assert_not_awaited()


