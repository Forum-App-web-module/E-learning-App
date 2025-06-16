import pytest
from unittest.mock import AsyncMock, patch
from services.user_service import get_hash_by_email
from repositories.user_repo import BadRequest
from repositories.user_repo import (
    insert_user_repo,
    get_account_by_email_repo,
    get_user_by_id_repo,
    email_exists_repo,
    get_role_by_email_repo
)
from data.models import UserRole, StudentRegisterData, TeacherRegisterData

@pytest.mark.asyncio
class TestGetHashByEmail:
    async def test_get_hash_by_email_returns_password(self):
        # Arrange
        email = "test@example.com"

        mock_read_query = AsyncMock(return_value=[["hashed_password"]])

        # Act
        result = await get_hash_by_email(email, get_data_func=mock_read_query)

        # Assert
        assert result == "hashed_password"
        mock_read_query.assert_awaited_once()

@pytest.mark.asyncio
class TestInsertUserRepo:
    async def test_insert_user_repo_student(self):
        # Arrange
        hashed_password = "hashed_pass"
        fake_id = 13

        student_data = StudentRegisterData(email="student@example.com", password=hashed_password)

        # Act & Assert
        with patch("repositories.user_repo.insert_query", new_callable=AsyncMock) as mock_insert_query:
            mock_insert_query.return_value = fake_id

            role, user_id = await insert_user_repo(student_data, hashed_password)

            assert role == UserRole.STUDENT
            assert user_id == fake_id
            mock_insert_query.assert_awaited_once()

            _, values = mock_insert_query.call_args.args
            assert values == (student_data.email, hashed_password)

    async def test_insert_user_repo_teacher(self):
        # Arrange
        hashed_password = "hashed_pass"
        fake_id = 17

        teacher_data = TeacherRegisterData(
            email="teacher@example.com",
            password=hashed_password,
            mobile="0333111000",
            linked_in_url="http://linkedin.com/in/teacher"
        )

        # Act & Assert
        with patch("repositories.user_repo.insert_query", new_callable=AsyncMock) as mock_insert_query:
            mock_insert_query.return_value = fake_id

            role, user_id = await insert_user_repo(teacher_data, hashed_password)

            assert role == UserRole.TEACHER
            assert user_id == fake_id
            mock_insert_query.assert_awaited_once()

            _, values = mock_insert_query.call_args.args
            assert values == (
                teacher_data.email,
                hashed_password,
                teacher_data.mobile,
                teacher_data.linked_in_url
            )

    async def test_insert_user_repo_invalid_type_returns_bad_request(self):
        # Arrange
        bad_data = object()  # not StudentRegisterData nor TeacherRegisterData

        # Act
        result = await insert_user_repo(bad_data, "fakepass")

        # Assert
        assert isinstance(result, BadRequest)

@pytest.mark.asyncio
class TestGetAccountByEmailRepo:
    async def test_returns_first_result(self):
        # Arrange
        email = "user@example.com"
        role = "student"
        fake_result = [{"id": 1, "email": email}]

        mock_read_query = AsyncMock(return_value=fake_result)

        # Act
        result = await get_account_by_email_repo(email, role, get_data_func=mock_read_query)

        # Assert
        assert result == fake_result[0]
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (email,)

    async def test_returns_none_if_no_result(self):
        # Arrange
        email = "user@example.com"
        role = "teacher"

        mock_read_query = AsyncMock(return_value=[])

        # Act
        result = await get_account_by_email_repo(email, role, get_data_func=mock_read_query)

        # Assert
        assert result is None
        mock_read_query.assert_awaited_once()

    async def test_raises_value_error_for_invalid_role(self):
        # Arrange
        email = "user@example.com"
        invalid_role = "unknown"

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported role"):
            await get_account_by_email_repo(email, invalid_role)


@pytest.mark.asyncio
class TestGetUserByIdRepo:
    async def test_returns_first_result(self):
        # Arrange
        user_id = 13
        role = "admin"
        fake_result = [{"id": user_id, "email": "admin@example.com"}]

        mock_read_query = AsyncMock(return_value=fake_result)

        # Act
        result = await get_user_by_id_repo(user_id, role, get_data_func=mock_read_query)

        # Assert
        assert result == fake_result[0]
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (user_id,)

    async def test_returns_none_if_no_result(self):
        # Arrange
        user_id = 13
        role = "teacher"

        mock_read_query = AsyncMock(return_value=[])

        # Act
        result = await get_user_by_id_repo(user_id, role, get_data_func=mock_read_query)

        # Assert
        assert result is None
        mock_read_query.assert_awaited_once()

@pytest.mark.asyncio
class TestEmailExistsRepo:
    async def test_returns_true_if_result(self):
        # Arrange
        email = "test@example.com"
        mock_read_query = AsyncMock(return_value=[{"email": email}])

        # Act
        result = await email_exists_repo(email, get_data_func=mock_read_query)

        # Assert
        assert result is True
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (email, email, email)

    async def test_returns_false_if_no_result(self):
        # Arrange
        email = "test@example.com"
        mock_read_query = AsyncMock(return_value=[])

        # Act
        result = await email_exists_repo(email, get_data_func=mock_read_query)

        # Assert
        assert result is False
        mock_read_query.assert_awaited_once()

@pytest.mark.asyncio
class TestGetRoleByEmailRepo:
    async def test_returns_first_role_found(self):
        # Arrange
        email = "test@example.com"
        # Simulate: found in students
        mock_read_query = AsyncMock(side_effect=[
            [{"1": 1}],  # students -> found
            [],          # teachers -> skipped
            []           # admins -> skipped
        ])

        # Act
        result = await get_role_by_email_repo(email, get_data_func=mock_read_query)

        # Assert
        assert result == "student"
        assert mock_read_query.await_count == 1  # stops at first found

    async def test_checks_all_tables_and_returns_role(self):
        # Arrange
        email = "test@example.com"
        # Simulate: not in students, but found in teachers
        mock_read_query = AsyncMock(side_effect=[
            [],           # students -> not found
            [{"1": 1}],   # teachers -> found
            []            # admins -> skipped
        ])

        # Act
        result = await get_role_by_email_repo(email, get_data_func=mock_read_query)

        # Assert
        assert result == "teacher"
        assert mock_read_query.await_count == 2

    async def test_returns_none_if_not_found_in_any(self):
        # Arrange
        email = "test@example.com"
        mock_read_query = AsyncMock(side_effect=[
            [], [], []  # students, teachers, admins -> none found
        ])

        # Act
        result = await get_role_by_email_repo(email, get_data_func=mock_read_query)

        # Assert
        assert result is None
        assert mock_read_query.await_count == 3

