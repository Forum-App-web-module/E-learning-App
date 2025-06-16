from fastapi import APIRouter, Depends, Security, Request
from fastapi.security.utils import get_authorization_scheme_param
from services.course_service import (
    get_all_courses_per_teacher_service,
    get_all_courses_per_student_service,
    create_course_service,
    update_course_service,
    get_all_courses_service)
from services.section_service import (
    create_section_service,update_section_service, get_all_sections_per_course_service,
    hide_section_service,is_student_allowed_to_view_sections)
from data.models import CourseCreate, CourseBase, CourseUpdate, SectionCreate, SectionUpdate, CourseFilterOptions, UserRole, TeacherCourseFilter, StudentCourseFilter
from fastapi.security import OAuth2PasswordBearer
from common.responses import Unauthorized, NotFound, Created, Successful, Forbidden
from security.auth_dependencies import get_current_user
from services.teacher_service import get_teacher_by_email, validate_teacher_verified_and_activated
from router_helper import router_helper
from typing import Optional


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

courses_router = APIRouter(prefix="/courses", tags=["courses"])

@courses_router.get("/public")
async def get_all_courses(request: Request, filters: CourseFilterOptions = Depends()):
    """
List all public courses.

Returns public courses for anonymous users.
If a student is authenticated and subscribed, premium courses are included.
"""
    auth: Optional[str] = request.headers.get("Authorization") #get auth header
    student_id = None

    if auth:
        scheme, token = get_authorization_scheme_param(auth) #get the scheme and token from header
        if scheme.lower() == "bearer" and token:
            try:
                payload = await get_current_user(token)
                if payload.get("role") == UserRole.STUDENT:
                    student_id = payload.get("id")
            except Exception:
                pass  # for anonymous users

    return await get_all_courses_service(filters, student_id)


@courses_router.get("/student")
async def get_all_courses_per_student(filters: StudentCourseFilter = Depends(), payload: dict = Depends(get_current_user)):
    """
List all courses the authenticated student is enrolled in.

Returns:
    A list of student-specific enrolled courses.
"""
    if payload.get("role") != UserRole.STUDENT:
        return Unauthorized(content="Only students can view the courses they are enrolled to.")
    
    return await get_all_courses_per_student_service(payload.get("id"), filters)

@courses_router.get("/teacher")
async def get_all_courses_per_teacher(filters: TeacherCourseFilter = Depends(), payload: dict = Depends(get_current_user)):
    """
List all courses created by the authenticated teacher.

Returns:
    A list of teacher-owned courses.
"""
    if payload.get("role") != UserRole.TEACHER:
        return Unauthorized(content="Only teachers can view the courses they own.")    
    
    return await get_all_courses_per_teacher_service(payload.get("id"), filters)

@courses_router.post("/")
async def create_course(course_data: CourseBase, payload: dict = Security(get_current_user)):
    """
Create a new course (Teacher only).

Only verified and active teachers can create courses.
Owner ID is inferred from the authenticated token.
"""
    if payload["role"] != UserRole.TEACHER:
        return Unauthorized(content="Only teachers can create courses")    
    
    id = await router_helper.get_teacher_id(payload.get("email"))
    if not await validate_teacher_verified_and_activated(id):
        return Forbidden(content="Account is not verified/activated still. Please verify your email first.")
    new_course = CourseCreate(**course_data.model_dump(), owner_id=id)
    new_id = await create_course_service(new_course)

    return Created(content={"new_id" : new_id, "message": f"Course with id {new_id} created"})

@courses_router.patch("/{course_id}")
async def update_course(course_id: int, updates: CourseUpdate, payload: dict = Security(get_current_user)):
    """
    Update a course by ID\n
    Requirements:\n
        - valid access token\n
        - role: teacher\n
        - only course owner can update it\n
    Accepts partial updates of course fields.\n
    Only include the fields you want to change in the request body. \n
    Fields left out will retain their current values.\n

    ❗ Important:\n
    Do NOT submit fields with default or placeholder values like `"description": "string"`,
    as these will overwrite real data.\n
    For example, to update only the course title, 
    send:\n
    
        {
            "title": "New Title"
        }
        
    """
    if payload["role"] != UserRole.TEACHER:
        return Unauthorized(content="Only teachers can update courses")

    id = await router_helper.get_teacher_id(payload.get("email"))
    
    validated = await router_helper.verify_course_owner(course_id, id)

    if not validated:
        return Unauthorized(content="Only course owners can perform this action")

    updated = await update_course_service(course_id, updates)

    if not updated:
        return NotFound(content="Course not found")
    
    return Successful(content={"message": f"Course with id {course_id} updated"})


@courses_router.post("/{course_id}/sections")
async def create_section(course_id: int, section: SectionCreate, payload: dict = Security(get_current_user)):
    """
Create a new section for a course.

Only the course owner can create sections.
Requires title, description, and content in the request body.

"""
    id = await router_helper.get_teacher_id(payload.get("email"))
    
    await router_helper.verify_course_owner(course_id, id)

    new_section = await create_section_service(course_id, section)

    return Created(content={"section": new_section})

@courses_router.patch("/{course_id}/{section_id}")
async def update_section(course_id: int, section_id: int, updates: SectionUpdate, payload: dict = Security(get_current_user)):
    """
    Update a course section by ID\n
    Requirements:\n
        - valid access token\n
        - role: teacher\n
        - only course owner can update the section\n
    Accepts partial updates of section fields.\n
    Only include the fields you want to change in the request body. \n
    Fields left out will retain their current values.\n

    ❗ Important:\n
    Do NOT submit fields with default or placeholder values like `"description": "string"`,
    as these will overwrite real data.\n
    For example, to update only the course title, 
    send:\n
    
        {
            "title": "New Title"
        }
        
    """
    id = await router_helper.get_teacher_id(payload.get("email"))
    
    await router_helper.verify_course_owner(course_id, id)

    updated = await update_section_service(section_id, updates)

    if not updated:
        return NotFound(content="Section not found")
    
    return Successful(content={"message": f"Section with id {section_id} updated"})

@courses_router.put("/{course_id}/{section_id}")
async def hide_section(course_id: int, section_id: int, payload: dict = Security(get_current_user)):
    """
Hide a section from student view.

Only the course owner (teacher) can hide a section.
Useful for temporarily removing a section from visibility.
"""

    teacher_id = await router_helper.get_teacher_id(payload.get("email"))
    
    await router_helper.verify_course_owner(course_id, teacher_id)

    result = await hide_section_service(section_id)
    if not result:
        return NotFound
    
    return Successful(content=f"Section {section_id} has been hidden")

@courses_router.get("/{course_id}/sections")
async def get_all_course_sections(
    course_id: int,
    sort_by: str = "id",
    order: str = "asc",
    payload: dict = Security(get_current_user)):
    """
Get all sections for a specific course.

Access is role-based:
- Admins: All sections
- Teachers: All if they own the course
- Students: Only if enrolled, and section is visible

Query params:
    sort_by: Field to sort by (default: 'id')
    order: Sort order (asc/desc)
"""

    user_role = payload.get("role")

    if user_role == UserRole.ADMIN:
        return await get_all_sections_per_course_service(course_id, sort_by, order)

    if user_role == UserRole.TEACHER:
        email = payload.get("email")
        teacher = await get_teacher_by_email(email)

        if not teacher:
            return Unauthorized(content="Access denied")
    
        is_owner = await router_helper.verify_course_owner(course_id, teacher["id"])
        if not is_owner:
            return  await get_all_sections_per_course_service(course_id, sort_by, order)
        
        return await get_all_sections_per_course_service(course_id, sort_by, order)
    
    if user_role == UserRole.STUDENT:
        student_id = payload.get("id")
        allowed = await is_student_allowed_to_view_sections(course_id, student_id)

        if not allowed:
            return Forbidden(content="Access to course sections is accessible for enrolled users only")
        
        return await get_all_sections_per_course_service(course_id, sort_by, order)
    
    return Forbidden("Only enrolled students, owners, or admins can access course sections.")




