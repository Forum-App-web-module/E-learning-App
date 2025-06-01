from fastapi import APIRouter, UploadFile, File, Header, Depends
from config.cloudinary_config import upload_avatar
from security.auth_dependencies import get_current_user
from controllers import student_controller
from common import responses
from services.student_service import update_avatar_url, get_student_by_email
from fastapi.security import OAuth2PasswordBearer
from services.subscription_service import subscribe, is_subscribed
from services.course_service import enroll_course, count_premium_enrollments, get_course_by_id_service
from data.models import SubscriptionResponse


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


from fastapi.security import OAuth2PasswordRequestForm

@students_router.post("/subscribe")
async def subscribe_student(payload: str = Depends(get_current_user)):
    student = await get_student_by_email(payload["sub"])
    subscription = await subscribe(student)
    return responses.Created(content=SubscriptionResponse(**subscription).model_dump(mode="json"))

@students_router.post("/enroll")
async def enroll(course_id: int, payload: str = Depends(get_current_user)):

    # Checking if course is premium
    course = get_course_by_id_service(course_id)
    if course[5] == True:
        if is_subscribed(student_id):

            # Checking premium courses enrollment count.
            premium_enrollments_count = count_premium_enrollments((payload.get("email")))
            if premium_enrollments_count >= 5:
                return responses.Unauthorized(content="Student is already enrolled to 5 premium courses. First complete or cancel enrollment.")

    # Creating enrollment.
    endrollment_id = enroll_course()
    pass
    

