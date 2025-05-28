from fastapi import APIRouter, UploadFile, File, Header, Depends
from data.cloudinary_config import upload_avatar
from security.jwt_auth import verify_access_token
from security.auth_dependencies import get_current_user
from controllers import student_controller
from common import responses
from services.student_service import update_avatar_url


students_router = APIRouter(prefix="/students", tags=["students"])


@students_router.get("/")
async def get_students(payload: str = Depends(get_current_user)):
    return await student_controller.get_student_by_email_controller(payload["sub"])


@students_router.post('/avatar')
def upload_avatar_photo(file: UploadFile = File(...), token: str = Header()):
    payload = verify_access_token(token)
    email = payload.get("email")

    # Uploading and generating URL 
    url = upload_avatar(file, email)

    # Updating URL in datebase
    update_avatar_url(url, email)

    return responses.Created(content={"message": f"New User is registered." })
