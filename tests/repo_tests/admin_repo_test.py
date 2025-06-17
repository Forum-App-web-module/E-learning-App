import pytest
from unittest.mock import AsyncMock
from repositories.admin_repo import change_account_state_repo, soft_delete_course_repo
from data.models import Action_UserRole, Action

@pytest.mark.asyncio
class TestChangeAccountStateRepo:
    async def test_should_call_update_query_with_correct_query_and_params(self):
        # Arrange
        user_id = 11
        role = Action_UserRole.student
        action = Action.activate
        fake_row_count = 1

        mock_update_query = AsyncMock(return_value=fake_row_count)
        # Act
        result = await change_account_state_repo(role, action, user_id, update_date_func=mock_update_query)

        # Assert
        assert result == fake_row_count
        mock_update_query.assert_awaited_once()

@pytest.mark.asyncio
class TestSoftDeleteCourseRepo:
    async def test_should_call_update_query_with_correct_query_and_params(self):
        # Arrange
        course_id = 11
        fake_row_count = 1

        mock_update_query = AsyncMock(return_value=fake_row_count)

        # Act
        result = await soft_delete_course_repo(course_id, update_date_func=mock_update_query)

        # Assert
        assert result == fake_row_count
        mock_update_query.assert_awaited_once()


