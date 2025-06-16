import pytest
from unittest.mock import patch, AsyncMock
from services.course_service import (
    get_all_courses_service,
    get_course_by_id_service
)
from data.models import CourseFilterOptions


@pytest.mark.asyncio
class TestGetAllCoursesServiceShould:
    async def test_with_student_id_calls_subscription_check(self):
        filters = CourseFilterOptions()
        student_id = 42

        with patch("services.course_service.validate_subscription_repo", new_callable=AsyncMock) as mock_validate, \
             patch("services.course_service.get_all_courses_repo", new_callable=AsyncMock) as mock_repo:
            mock_validate.return_value = True
            mock_repo.return_value = []

            result = await get_all_courses_service(filters, student_id)

            mock_validate.assert_awaited_once_with(student_id)
            mock_repo.assert_awaited_once_with(filters, True)
            assert result == []

    async def test_without_student_id_skips_subscription_check(self):
        filters = CourseFilterOptions()

        with patch("services.course_service.get_all_courses_repo", new_callable=AsyncMock) as mock_repo:
            mock_repo.return_value = ["course1", "course2"]

            result = await get_all_courses_service(filters)

            mock_repo.assert_awaited_once_with(filters, False)
            assert result == ["course1", "course2"]


@pytest.mark.asyncio
class TestGetCourseByIdServiceShould:
    async def test_returns_course(self):
        with patch("services.course_service.get_course_by_id_repo", new_callable=AsyncMock) as mock_repo:
            mock_repo.return_value = {"id": 1, "name": "Test Course"}

            result = await get_course_by_id_service(1)

            mock_repo.assert_awaited_once_with(1)
            assert result["id"] == 1