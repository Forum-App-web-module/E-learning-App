from fastapi import APIRouter, UploadFile, File, Header, Depends
from config.cloudinary_config import upload_avatar
from security.auth_dependencies import get_current_user
from controllers import student_controller
from common import responses
from services.student_service import update_avatar_url, get_student_by_email
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


students_router = APIRouter(prefix="/students", tags=["students"])


@students_router.get("/")
async def get_students(payload: str = Depends(get_current_user)):
    return await student_controller.get_student_by_email_controller(payload["sub"])


@students_router.post('/avatar')
async def upload_avatar_photo(file: UploadFile = File(...), payload: str = Depends(get_current_user) ):

    email = payload.get("email")

    # Uploading and generating URL 
    url = upload_avatar(file, email)

    # Updating URL in datebase
    update_avatar_url(url, email)

    student_profile = await get_student_by_email(email)

    return responses.Created(content = student_profile)
