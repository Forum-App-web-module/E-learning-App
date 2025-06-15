import pytest
from unittest.mock import patch, AsyncMock

from services.enrollment_service import get_enrollment_by_id, EnrollmentResponse


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
