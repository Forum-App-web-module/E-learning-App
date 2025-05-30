from fastapi import APIRouter, Depends, Security
#from controllers.course_controller
from services.course_service import get_all_courses_service, get_course_by_id_service, create_course_service
from data.models import CourseCreate, Course, CourseBase
from security.jwt_auth import verify_access_token
from fastapi.security import OAuth2PasswordBearer
from data.database import read_query
from common.responses import Unauthorized, NotFound
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

courses_router = APIRouter(prefix="/courses", tags=["courses"])


@courses_router.get("/")
async def get_all_courses():
    return await get_all_courses_service()

@courses_router.post("/")
async def create_course(course_data: CourseBase, token: str = Depends(oauth2_scheme)): # using Security instead of Depends to allow token usage in Swagger
    user = verify_access_token(token)
    email = user.get("sub")

    if not email:
        return Unauthorized
    # The query will be moved to a repo/service later
    query = """SELECT id from v1.teachers WHERE email = $1"""
    result = await read_query(query, (email,))
    if not result:
        raise NotFound("Teacher not found")
    
    owner_id = result[0]["id"]

    new_course = CourseCreate(**course_data.model_dump(), owner_id=owner_id)
    return await create_course_service(new_course)


