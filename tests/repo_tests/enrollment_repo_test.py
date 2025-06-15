import pytest
from unittest.mock import AsyncMock

from repositories.enrollments_repo import get_enrollment_by_id_repo


@pytest.mark.asyncio
class TestGetEnrollmentByIdRepo:
    async def test_found(self):
        # Arrange
        fake_result = [{"id": 1, "student_name": "Jane Doe", "course_id": 4}]
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


