import pytest
from unittest.mock import AsyncMock, patch

from services.student_service import update_student_service


@pytest.mark.asyncio
class TestUpdateStudentService:
    async def test_should_update_student_and_return_account(self):
        # Arrange
        fake_account = {"email": "test@example.com", "first_name": "Poodle"}
        with patch(
            "services.student_service.update_student_data_repo", new_callable=AsyncMock
        ) as mock_update, patch(
            "services.student_service.get_account_by_email_repo", new_callable=AsyncMock
        ) as mock_get_account:
            mock_get_account.return_value = fake_account

            # Act
            result = await update_student_service(
                first_name="Poodle",
                last_name="Name",
                avatar_url="http://image",
                user_email="test@example.com",
                user_role="student"
            )

            # Assert
            mock_update.assert_awaited_once_with(
                "Poodle", "Name", "http://image", "test@example.com"
            )
            mock_get_account.assert_awaited_once_with("test@example.com", "student")
            assert result == fake_account



