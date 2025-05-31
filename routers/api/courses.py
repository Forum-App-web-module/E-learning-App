from fastapi import APIRouter, Depends, Security
#from controllers.course_controller
from services.course_service import get_all_courses_per_teacher_service, get_course_by_id_service, create_course_service, verify_course_owner, update_course_service
from services.section_service import create_section_service
from data.models import CourseCreate, Course, CourseBase, CourseUpdate, SectionCreate, SectionOut
from fastapi.security import OAuth2PasswordBearer
from data.database import read_query
from common.responses import Unauthorized, NotFound, Created, Successful
from security.auth_dependencies import get_current_user
from services.teacher_service import get_teacher_by_email


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

courses_router = APIRouter(prefix="/courses", tags=["courses"])


@courses_router.get("/{teacher_id}")
async def get_all_courses(teacher_id):
    return await get_all_courses_per_teacher_service(teacher_id)

@courses_router.post("/")
async def create_course(course_data: CourseBase, payload: dict = Security(get_current_user)): 
    """
    Create a new course:\n
    Requrements:\n
        valid access token \n
        role: teacher \n
    Owner ID is extracted from the token and linked to the course.\n
    """
    email = payload.get("sub")
    id = await get_teacher_by_email(email)

    new_course = CourseCreate(**course_data.model_dump(), owner_id=id[0])
    new_id = await create_course_service(new_course)

    return Created(content={"new_id" : new_id, "message": f"Course with id {new_id} created"})

@courses_router.patch("/{course_id}")
async def update_course(course_id: int, updates: CourseUpdate, payload: dict = Security(get_current_user)):
    """
    Update a course by ID\n
    Requrements:\n
        valid access token\n
        role: teacher\n
        only course owner can update it\n
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

    email = payload.get("sub")
    teacher = await get_teacher_by_email(email)

    if not teacher:
        raise Unauthorized()
    
    await verify_course_owner(course_id, teacher["id"])

    updated = await update_course_service(course_id, updates)

    if not updated:
        raise NotFound(content="Course not found")
    
    return Successful(content={"message": f"Course with id {course_id} updated"})


@courses_router.post("/{course_id}/sections")
async def create_section(course_id: int, section: SectionCreate, payload: dict = Security(get_current_user)):

    email = payload.get("sub")
    teacher = await get_teacher_by_email(email)

    if not teacher:
        raise Unauthorized(content="Only teachers allowed for this action")
    
    await verify_course_owner(course_id, teacher["id"])

    new_section = await create_section_service(course_id, section)

    return Created(content={"section": new_section})