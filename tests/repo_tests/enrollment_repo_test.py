import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from repositories.enrollments_repo import (
    create_enrollment_repo,
    confirm_enrollment_repo,
    get_enrollment_by_id_repo,
    get_enrollment_by_student_course_repo,
    unenroll_student_repo
)


@pytest.mark.asyncio
class TestRepoCreateEnrollment:
    async def test_returns_rowcount_when_success(self):
        # Arrange
        student_id = 13
        course_id = 121
        fake_result = 1
        mock_insert_query = AsyncMock(return_value=fake_result)

        # Act
        result = await create_enrollment_repo(course_id, student_id, insert_data_func=mock_insert_query)

        # Assert
        assert result == fake_result
        mock_insert_query.assert_awaited_once_with(
            """INSERT INTO v1.enrollments (student_id, course_id) 
               VALUES ($1,$2) 
               RETURNING id""",
            (student_id, course_id)
        )

    async def test_returns_none_when_not_success(self):
        # Arrange
        student_id = 13
        course_id = 121
        mock_insert_query = AsyncMock(return_value=None)

        # Act
        result = await create_enrollment_repo(course_id, student_id, insert_data_func=mock_insert_query)

        # Assert
        assert result is None

@pytest.mark.asyncio
class TestRepoConfirmEnrollment:
    async def test_should_call_update_query_with_correct_query_and_params(self):
        enrollment_id = 123
        fake_row_count = 1
        fake_timestamp = datetime(2025, 6, 15, 11, 59, 59)

        mock_update_query = AsyncMock(return_value=fake_row_count)

        # Patching datetime.now()
        with patch("repositories.enrollments_repo.datetime") as mock_datetime:
            mock_datetime.now.return_value = fake_timestamp

            result = await confirm_enrollment_repo(enrollment_id, update_data_func=mock_update_query)

            # Should return row count from update query
            assert result == fake_row_count

            # Should call update query with correct SQL and params
            mock_update_query.assert_awaited_once_with(
                """UPDATE v1.enrollments 
               SET is_approved = $1, 
                   approved_at = $2 
               WHERE id = $3""",
                (True, fake_timestamp, enrollment_id)
            )

@pytest.mark.asyncio
class TestGetEnrollmentByIdRepo:
    async def test_found(self):
        # Arrange
        fake_result = [{"id": 1, "student_name": "Poodle VonStrauss", "course_id": 4}]
        mock_read_query = AsyncMock(return_value=fake_result)

        # Act
        result = await get_enrollment_by_id_repo(1, read_data_func=mock_read_query)

        # Assert
        assert result == fake_result[0]
        mock_read_query.assert_awaited_once()

    async def test_not_found(self):
        # Arrange
        mock_read_query = AsyncMock(return_value=[])

        # Act
        result = await get_enrollment_by_id_repo(1, read_data_func=mock_read_query)

        # Assert
        assert result is None
        mock_read_query.assert_awaited_once()

@pytest.mark.asyncio
class TestEnrollmentByStudentCourseRepo:

    async def test_returns_first_row_when_found(self):
        # Arrange
        student_id = 1
        course_id = 11
        fake_result = [{"id": 12}]

        mock_read_query = AsyncMock(return_value=fake_result)

        # Act
        result = await get_enrollment_by_student_course_repo(student_id, course_id, read_data_func=mock_read_query)

        # Assert
        assert result == fake_result[0]
        mock_read_query.assert_awaited_once_with(
            """SELECT id 
               FROM v1.enrollments 
               WHERE student_id = $1 
                 AND course_id = $2""",
            (student_id, course_id)
        )

    async def test_returns_none_when_not_found(self):
        # Arrange
        student_id = 2
        course_id = 22
        mock_read_query = AsyncMock(return_value=[])

        # Act
        result = await get_enrollment_by_student_course_repo(student_id, course_id, read_data_func=mock_read_query)

        # Assert
        assert result is None
        mock_read_query.assert_awaited_once_with(
            """SELECT id 
               FROM v1.enrollments 
               WHERE student_id = $1 
                 AND course_id = $2""",
            (student_id, course_id)
        )

@pytest.mark.asyncio
class TestUnenrollStudentRepo:
    async def test_returns_rowcount_when_success(self):
        # Arrange
        enrollment_id = 1
        drop_out = False
        fake_result = 1
        mock_update_query = AsyncMock(return_value=1)

        # Act
        result = await unenroll_student_repo(enrollment_id, drop_out, update_data_func=mock_update_query)

        #Assert
        assert result == fake_result
        mock_update_query.assert_awaited_once_with(
            """UPDATE v1.enrollments
               SET drop_out = $2, 
                   completed_at = now() 
               WHERE id = $1""",
            (enrollment_id, drop_out,)
        )
