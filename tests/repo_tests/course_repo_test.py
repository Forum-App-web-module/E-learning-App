import pytest
from unittest.mock import AsyncMock
from repositories.course_repo import (
    get_all_courses_repo,
    get_course_by_id_repo,
    get_all_courses_per_teacher_repo,
    get_all_student_courses_repo,
    insert_course_repo,
    update_course_data_repo,
    count_premium_enrollments_repo,
    get_course_rating_repo,
    admin_course_view_repo,
    complete_course_repo
)
from data.models import CourseFilterOptions, TeacherCourseFilter, StudentCourseFilter, CourseCreate, CourseUpdate


@pytest.mark.asyncio
async def test_get_all_courses_repo():
    filters = CourseFilterOptions()
    mock_func = AsyncMock(return_value=["course1", "course2"])
    result = await get_all_courses_repo(filters, premium=True, get_data_func=mock_func)
    assert result == ["course1", "course2"]
    mock_func.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_course_by_id_repo():
    mock_func = AsyncMock(return_value=[{"id": 1}])
    result = await get_course_by_id_repo(1, get_data_func=mock_func)
    assert result["id"] == 1
    mock_func.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_courses_per_teacher_repo():
    filters = TeacherCourseFilter()
    teacher_id = 1
    mock_func = AsyncMock(return_value=[])
    result = await get_all_courses_per_teacher_repo(teacher_id, filters, get_data_func=mock_func)
    assert result == []
    mock_func.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_student_courses_repo():
    student_id = 1
    filters = StudentCourseFilter()
    mock_func = AsyncMock(return_value=["courseA"])
    result = await get_all_student_courses_repo(student_id, filters, get_data_func=mock_func)
    assert result == ["courseA"]
    mock_func.assert_awaited_once()


@pytest.mark.asyncio
async def test_insert_course_repo():
    data = CourseCreate(
        title="Test",
        description="Test course",
        tags="test,course",
        picture_url="http://example.com/pic.png",
        is_premium=False,
        owner_id=1
    )
    mock_func = AsyncMock(return_value=123)
    result = await insert_course_repo(data, insert_data_func=mock_func)
    assert result == 123
    mock_func.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_course_data_repo():
    data = CourseUpdate(title="Updated")
    course_id = 1
    mock_func = AsyncMock(return_value=True)
    result = await update_course_data_repo(course_id, data, update_data_func=mock_func)
    assert result is True
    mock_func.assert_awaited_once()


@pytest.mark.asyncio
async def test_count_premium_enrollments_repo():
    course_id = 1
    mock_func = AsyncMock(return_value=5)
    result = await count_premium_enrollments_repo(course_id, count_data_func=mock_func)
    assert result == 5
    mock_func.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_course_rating_repo():
    course_id = 1
    mock_func = AsyncMock(return_value=4.5)
    result = await get_course_rating_repo(course_id, get_data_func=mock_func)
    assert result == 4.5
    mock_func.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_course_view_repo():
    mock_func = AsyncMock(return_value=[{"id": 1}])
    result = await admin_course_view_repo(
        title_filter="",
        teacher_id=None,
        student_id=None,
        limit=10,
        offset=0,
        get_data_func=mock_func
    )
    assert result == [{"id": 1}]
    mock_func.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_course_repo():
    student_id = 10
    course_id = 20
    mock_func = AsyncMock(return_value=True)
    result = await complete_course_repo(student_id, course_id, update_data_func=mock_func)
    assert result is True
    mock_func.assert_awaited_once()
