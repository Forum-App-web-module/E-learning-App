from fastapi import APIRouter, Depends, Security
from services.course_service import (
    get_all_courses_per_teacher_service,
    get_all_courses_per_student_service,
    get_course_by_id_service,
    create_course_service,
    verify_course_owner,
    update_course_service,
    get_all_public_courses_service)
from services.section_service import create_section_service, update_section_service, get_all_sections_per_course_service, hide_section_service
from data.models import CourseCreate, CourseBase, CourseUpdate, SectionCreate, SectionOut, SectionUpdate, CourseFilterOptions
from fastapi.security import OAuth2PasswordBearer
from common.responses import Unauthorized, NotFound, Created, Successful, Forbidden
from security.auth_dependencies import get_current_user
from services.teacher_service import get_teacher_by_email, validate_teacher_verified_and_activated
from router_helper import router_helper
from typing import Optional


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

courses_router = APIRouter(prefix="/courses", tags=["courses"])

@courses_router.get("/public")
async def get_public_courses(filters: CourseFilterOptions = Depends()):
    """List all public courses, accessible for non autheticated users"""

    return await get_all_public_courses_service(filters)

@courses_router.get("/student")
async def get_all_courses_per_student(payload: dict = Depends(get_current_user)):
    """
    Returns a list with all courses owned by the student\n
    Params: payload

    """
    return await get_all_courses_per_student_service(payload.get("id"))

@courses_router.get("/teacher")
async def get_all_courses_per_teacher(payload: dict = Depends(get_current_user)):
    """
    Returns a list with all courses owned by the teacher\n
    Params: payload

    """
    return await get_all_courses_per_teacher_service(payload.get("id"))

@courses_router.post("/")
async def create_course(course_data: CourseBase, payload: dict = Security(get_current_user)): 
    """
    Create a new course:\n
    Requrements:\n
        valid access token \n
        role: teacher \n
    Owner ID is extracted from the token and linked to the course.\n
    """
    id = await router_helper.get_teacher_id(payload.get("email"))
    if not await validate_teacher_verified_and_activated(id):
        return Forbidden(content="Account is not verified/acticated still. Please verify your email first.")
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

    id = await router_helper.get_teacher_id(payload.get("email"))
    
    await verify_course_owner(course_id, id)

    updated = await update_course_service(course_id, updates)

    if not updated:
        return NotFound(content="Course not found")
    
    return Successful(content={"message": f"Course with id {course_id} updated"})


@courses_router.post("/{course_id}/sections")
async def create_section(course_id: int, section: SectionCreate, payload: dict = Security(get_current_user)):
    """
    Create a new section under a specific course.\n\n
    Valid access token is required\n
    - `course_id` comes from the route.\n
    - Body should include: title, content, description.\n
    - Authorization is required, and only the course owner can perform this action\n

    Return new section ID
    """
    id = await router_helper.get_teacher_id(payload.get("email"))
    
    await verify_course_owner(course_id, id)

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
    
    await verify_course_owner(course_id, id)

    updated = await update_section_service(section_id, updates)

    if not updated:
        return NotFound(content="Section not found")
    
    return Successful(content={"message": f"Section with id {section_id} updated"})

@courses_router.put("/{course_id}/{section_id}")
async def hide_section(course_id: int, section_id: int, payload: dict = Security(get_current_user)):

    teacher_id = await router_helper.get_teacher_id(payload.get("email"))
    
    await verify_course_owner(course_id, teacher_id)

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

    email = payload.get("email")
    teacher = await get_teacher_by_email(email)

    if not teacher:
        return Unauthorized()
    
    await verify_course_owner(course_id, teacher["id"])

    return  await get_all_sections_per_course_service(course_id, sort_by, order)




