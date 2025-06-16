import pytest
from unittest.mock import AsyncMock, patch
from common.responses import Forbidden
from data.models import UserRole
from services.teacher_service import validate_teacher_role

@pytest.mark.asyncio
class TestValidateTeacherRole:
    async def test_should_return_forbidden_when_not_teacher(self):
        # Arrange
        user_email = "test@example.com"
        fake_response = Forbidden(content="Only a Teacher user can perform this action")

        with patch("services.teacher_service.get_role_by_email_repo", new_callable=AsyncMock) as mock_repo:
            mock_repo.return_value = fake_response

            result = await validate_teacher_role(user_email)

            assert isinstance(result, Forbidden)
            mock_repo.assert_awaited_once_with(user_email)

    async def test_should_return_none_when_teacher(self):
        # Arrange
        user_email = "test@example.com"
        fake_response = UserRole.TEACHER

        with patch("services.teacher_service.get_role_by_email_repo", new_callable=AsyncMock) as mock_repo:
            mock_repo.return_value = fake_response

            result = await validate_teacher_role(user_email)

            assert result is None
            mock_repo.assert_awaited_once_with(user_email)



