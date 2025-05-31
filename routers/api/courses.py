from fastapi import APIRouter, Depends, Security
#from controllers.course_controller
from services.course_service import get_all_courses_service, get_course_by_id_service, create_course_service
from data.models import CourseCreate, Course, CourseBase
from fastapi.security import OAuth2PasswordBearer
from data.database import read_query
from common.responses import Unauthorized, NotFound, Created
from security.auth_dependencies import get_current_user
from services.teacher_service import get_teacher_by_email


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

courses_router = APIRouter(prefix="/courses", tags=["courses"])


@courses_router.get("/")
async def get_all_courses():
    return await get_all_courses_service()

@courses_router.post("/")
async def create_course(course_data: CourseBase, payload: str = Security(get_current_user)): 
    email = payload.get("sub")
    id = await get_teacher_by_email(email)

    new_course = CourseCreate(**course_data.model_dump(), owner_id=id[0])
    new_id = await create_course_service(new_course)

    return Created(content={"new_id" : new_id})

    # return 


    # # The query will be moved to a repo/service later
    # query = """SELECT id from v1.teachers WHERE email = $1"""
    # result = await read_query(query, (email,))
    # if not result:
    #     raise NotFound("Teacher not found")
    
    # owner_id = result[0]["id"]

    # new_course = CourseCreate(**course_data.model_dump(), owner_id=owner_id)
    # return await create_course_service(new_course)


