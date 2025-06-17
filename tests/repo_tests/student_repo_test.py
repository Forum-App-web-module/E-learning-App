import pytest
from unittest.mock import AsyncMock, patch
from datetime import date, datetime, timedelta
from repositories import student_repo
from data.models import Subscription


@pytest.mark.asyncio
class TestUpdateStudentDataRepo:

    async def test_should_call_update_query_with_correct_query_and_params(self):
        # Arrange
        first_name = "Poodle"
        last_name = "VonStrauss"
        avatar_url = "http://example.com/avatar.png"
        user_email = "poodle@example.com"

        fake_result = 1

        mock_update_query = AsyncMock(return_value=fake_result)

        # Act
        result = await student_repo.update_student_data_repo(
            first_name,
            last_name,
            avatar_url,
            user_email,
            update_data_func=mock_update_query
        )

        # Assert
        assert result == fake_result
        mock_update_query.assert_awaited_once_with(
            """
        UPDATE v1.students 
        SET first_name = COALESCE($1, first_name),
            last_name = COALESCE($2, last_name),
            avatar_url = COALESCE($3, avatar_url)
        WHERE email = $4
        """,
            (first_name, last_name, avatar_url, user_email)
        )

@pytest.mark.asyncio
class TestGetCoursesStudentAllRepo:

    async def test_should_use_correct_keywords_and_returns_courses_when_found(self):
        # Arrange
        student_id = 11
        fake_courses = [{"id": 1}, {"id": 2}]
        mock_read_query = AsyncMock(return_value=fake_courses)

        # Act
        result = await student_repo.get_courses_student_all_repo(student_id, get_data_func=mock_read_query)

        # Assert
        assert result == fake_courses
        mock_read_query.assert_awaited_once()

        # Inspecting the actual call args
        called_query, called_params = mock_read_query.call_args.args

        # Checking param tuple
        assert called_params == (student_id, )

        # Inspecting query keywords
        assert "SELECT" in called_query
        assert "FROM v1.courses" in called_query
        assert "LEFT JOIN" in called_query

    async def test_returns_none_when_no_courses_found(self):
        student_id = 33
        mock_read_query = AsyncMock(return_value=[])

        result = await student_repo.get_courses_student_all_repo(student_id, get_data_func=mock_read_query)

        assert result is None

        mock_read_query.assert_awaited_once()

@pytest.mark.asyncio
class TestGetCoursesProgressRepo:

    async def test_returns_courses_when_found(self):
        # Arrange
        student_id = 11
        fake_result = [{"course_id": 1, "progress_percentage": 50.0}]
        mock_read_query = AsyncMock(return_value=fake_result)

        # Act
        result = await student_repo.get_courses_progress_repo(student_id, get_data_func=mock_read_query)

        # Assert
        assert result == fake_result
        mock_read_query.assert_awaited_once()

        # Checking that the student_id was passed
        _, params = mock_read_query.call_args.args
        assert params == (student_id,)

    async def test_returns_none_when_no_courses_found(self):
        # Arrange
        student_id = 11
        mock_read_query = AsyncMock(return_value=[])

        # Act
        result = await student_repo.get_courses_progress_repo(student_id, get_data_func=mock_read_query)

        # Assert
        assert result is None
        mock_read_query.assert_awaited_once()

@pytest.mark.asyncio
class TestUpdateAvatarUrlRepo:

    async def test_returns_updated_rows_when_successful(self):
        # Arrange
        url = "https://example.com/avatar.jpg"
        email = "student@example.com"
        fake_row_count = 1

        mock_update_query = AsyncMock(return_value=fake_row_count)

        # Act
        result = await student_repo.update_avatar_url_repo(
            url, email, update_data_func=mock_update_query
        )

        # Assert
        assert result == fake_row_count
        mock_update_query.assert_awaited_once()

        _, params = mock_update_query.call_args.args
        assert params == (url, email)

@pytest.mark.asyncio
class TestSubscriptionRepo:
    async def test_subscribe_repo_returns_new_id(self):
        student_id = 1
        expire_date = datetime.now() + timedelta(days=365)
        subscription = Subscription(student_id=student_id, expire_date=expire_date)
        fake_id = 22

        mock_insert_query = AsyncMock(return_value=fake_id)

        result = await student_repo.subscribe_repo(student_id, subscription, insert_data_func=mock_insert_query)

        assert result == fake_id
        mock_insert_query.assert_awaited_once()

        _, params = mock_insert_query.call_args.args
        assert params == (student_id, subscription.expire_date)

    async def test_is_subscribed_repo_returns_subscription_if_found(self):
        student_id = 1
        fake_subscription = [{"id": 1, "student_id": student_id}]

        mock_read_query = AsyncMock(return_value=fake_subscription)

        result = await student_repo.is_subscribed_repo(student_id, get_data_func=mock_read_query)

        assert result == fake_subscription[0]
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (student_id,)

    async def test_is_subscribed_repo_returns_none_if_not_found(self):
        student_id = 1
        mock_read_query = AsyncMock(return_value=[])

        result = await student_repo.is_subscribed_repo(student_id, get_data_func=mock_read_query)

        assert result is None
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (student_id,)

    async def test_validate_subscription_repo_returns_true_if_active(self):
        student_id = 1
        mock_read_query = AsyncMock(return_value=[{"dummy": "value"}])

        result = await student_repo.validate_subscription_repo(student_id, get_data_func=mock_read_query)

        assert result is True
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (student_id,)

    async def test_validate_subscription_repo_returns_false_if_not_active(self):
        student_id = 1
        mock_read_query = AsyncMock(return_value=[])

        result = await student_repo.validate_subscription_repo(student_id, get_data_func=mock_read_query)

        assert result is False
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (student_id,)

@pytest.mark.asyncio
class TestCourseRatingRepo:
    async def test_rate_course_repo_returns_rating(self):
        student_id = 1
        course_id = 11
        rating_value = 5

        fake_rating = {"students_id": student_id, "courses_id": course_id, "rating": rating_value}
        mock_insert_query = AsyncMock(return_value=fake_rating)

        result = await student_repo.rate_course_repo(
            student_id, course_id, rating_value, insert_data_func=mock_insert_query
        )

        assert result == fake_rating
        mock_insert_query.assert_awaited_once()

        _, params = mock_insert_query.call_args.args
        assert params == (student_id, course_id, rating_value)

    async def test_allow_rating_repo_returns_true_if_allowed(self):
        student_id = 1
        course_id = 11

        mock_read_query = AsyncMock(return_value=[{"dummy": "row"}])

        result = await student_repo.allow_rating_repo(
            student_id, course_id, get_data_func=mock_read_query
        )

        assert result is True
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (student_id, course_id)

    async def test_allow_rating_repo_returns_false_if_not_allowed(self):
        student_id = 1
        course_id = 11

        mock_read_query = AsyncMock(return_value=[])

        result = await student_repo.allow_rating_repo(
            student_id, course_id, get_data_func=mock_read_query
        )

        assert result is False
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (student_id, course_id)

    async def test_check_enrollment_repo_returns_true_if_found(self):
        student_id = 1
        course_id = 11

        mock_read_query = AsyncMock(return_value=[{"dummy": "row"}])

        result = await student_repo.check_enrollment_repo(
            course_id, student_id, get_data_func=mock_read_query
        )

        assert result is True
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (course_id, student_id)

    async def test_check_enrollment_repo_returns_false_if_not_found(self):
        student_id = 1
        course_id = 11

        mock_read_query = AsyncMock(return_value=[])

        result = await student_repo.check_enrollment_repo(
            course_id, student_id, get_data_func=mock_read_query
        )

        assert result is False
        mock_read_query.assert_awaited_once()

        _, params = mock_read_query.call_args.args
        assert params == (course_id, student_id)