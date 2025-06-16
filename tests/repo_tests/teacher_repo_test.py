import pytest
from unittest.mock import AsyncMock
from repositories.teacher_repo import (
    update_teacher_repo,
    report_enrolled_students_repo,
    deactivate_course_repo,
    verify_email_repo,
    validate_teacher_verified_and_activated_repo
)

@pytest.mark.asyncio
class TestUpdateTeacherRepo:
    async def test_update_teacher_repo_returns_result(self):
        # Arrange
        mobile = "0333111000"
        linked_in_url = "https://linkedin.com/in/test"
        email = "teacher@example.com"

        mock_update_query = AsyncMock(return_value={"some": "result"})

        # Act
        result = await update_teacher_repo(
            mobile, linked_in_url, email, update_data_func=mock_update_query
        )

        # Assert
        assert result == {"some": "result"}
        mock_update_query.assert_awaited_once()

    async def test_update_teacher_repo_returns_none_when_empty(self):
        # Arrange
        mobile = "0333111000"
        linked_in_url = "https://linkedin.com/in/test"
        email = "teacher@example.com"

        mock_update_query = AsyncMock(return_value=None)

        # Act
        result = await update_teacher_repo(
            mobile, linked_in_url, email, update_data_func=mock_update_query
        )

        # Assert
        assert result is None
        mock_update_query.assert_awaited_once()

@pytest.mark.asyncio
class TestReportEnrolledStudentsRepo:
    async def test_report_enrolled_students_repo_returns_result(self):
        # Arrange
        mock_read_query = AsyncMock(return_value=[{"student_id": 1, "email": "poodle@example.com"}])
        owner_id = 22

        # Act
        result = await report_enrolled_students_repo(owner_id, get_data_func=mock_read_query)

        # Assert
        assert result == [{"student_id": 1, "email": "poodle@example.com"}]
        mock_read_query.assert_awaited_once()

    async def test_report_enrolled_students_repo_returns_none_when_empty(self):
        # Arrange
        mock_read_query = AsyncMock(return_value=None)
        owner_id = 22

        # Act
        result = await report_enrolled_students_repo(owner_id, get_data_func=mock_read_query)

        # Assert
        assert result is None
        mock_read_query.assert_awaited_once()

@pytest.mark.asyncio
class TestDeactivateCourseRepo:
    async def test_deactivate_course_repo_returns_result(self):
        # Arrange
        teacher_id = 1
        course_id = 222

        mock_update_query = AsyncMock(return_value={"id": 1})

        # Act
        result = await deactivate_course_repo(
            teacher_id, course_id, update_data_func=mock_update_query
        )

        # Assert
        assert result == {"id": 1}
        mock_update_query.assert_awaited_once()

    async def test_deactivate_course_repo_returns_none_when_empty(self):
        # Arrange
        teacher_id = 1
        course_id = 11

        mock_update_query = AsyncMock(return_value=None)

        # Act
        result = await deactivate_course_repo(
            teacher_id, course_id, update_data_func=mock_update_query
        )

        # Assert
        assert result is None
        mock_update_query.assert_awaited_once()


@pytest.mark.asyncio
class TestVerifyEmailRepo:
    async def test_verify_email_repo_returns_result(self):
        # Arrange
        teacher_id = 13

        mock_update_query = AsyncMock(return_value={"id": 1})

        # Act
        result = await verify_email_repo(
            teacher_id, update_data_func=mock_update_query
        )

        # Assert
        assert result == {"id": 1}
        mock_update_query.assert_awaited_once()


@pytest.mark.asyncio
class TestValidateTeacherVerifiedAndActivatedRepo:
    async def test_validate_teacher_verified_and_activated_repo_returns_result(self):
        # Arrange
        teacher_id = 13

        mock_read_query = AsyncMock(return_value=[{"id": 1, "email_verified": True}])

        # Act
        result = await validate_teacher_verified_and_activated_repo(
            teacher_id, get_data_func=mock_read_query
        )

        # Assert
        assert result == [{"id": 1, "email_verified": True}]
        mock_read_query.assert_awaited_once()

    async def test_validate_teacher_verified_and_activated_repo_returns_none_when_empty(self):
        # Arrange
        teacher_id = 13

        mock_read_query = AsyncMock(return_value=None)

        # Act
        result = await validate_teacher_verified_and_activated_repo(
            teacher_id, get_data_func=mock_read_query
        )

        # Assert
        assert result is None
        mock_read_query.assert_awaited_once()

