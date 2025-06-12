from fastapi import APIRouter, UploadFile, File, Header, Body, Depends
from config.mailJet_config import teacher_approve_enrollment
from config.cloudinary_config import upload_avatar
from security.auth_dependencies import get_current_user
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from services.course_service import enroll_course, count_premium_enrollments, get_course_by_id_service
from services.enrollment_service import unenroll_student_service
from services.student_service import (
    update_avatar_url,
    get_student_by_email,
    update_student_service,
    get_student_courses_service,
    get_student_courses_progress_service,
    rate_course_service
)
from services.teacher_service import get_teacher_by_id
from services.subscription_service import subscribe, is_subscribed
from data.models import SubscriptionResponse, StudentResponse, CourseStudentResponse, CoursesProgressResponse, TeacherResponse, CourseResponse
from common import responses

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

students_router = APIRouter(prefix="/students", tags=["students"])


@students_router.get("/")
async def get_students(payload: dict = Depends(get_current_user)):
    if payload.get("role") != "student":
        return responses.Forbidden(content="Only a Student user can perform this action")
    student = await get_student_by_email(payload.get("email"))
    return responses.Successful(content=StudentResponse(**student).model_dump(mode="json"))

@students_router.put("/account")
async def update_student(
        payload: dict = Depends(get_current_user),
        first_name = Body(min_length=2, max_length=20),
        last_name = Body(min_length=2, max_length=20),
        avatar_url = Body(pattern=r"^https?:\/\/.*\.(png|jpg|jpeg)$")
):
    if payload.get("role") != "student":
        return responses.Forbidden(content="Only a Student user can perform this action")

    student = await update_student_service(
        first_name,
        last_name,
        avatar_url,
        payload.get("email"),
        payload.get("role")
    )

    return responses.Successful(content=StudentResponse(**student).model_dump(mode="json"))

@students_router.get("/courses")
async def get_student_courses(payload: dict = Depends(get_current_user)):
    if payload.get("role") != "student":
        return responses.Forbidden(content="Only a Student user can perform this action")

    student_courses = await get_student_courses_service(payload.get("id"))
    student_courses_response = [CourseStudentResponse(**sc).model_dump(mode="json") for sc in student_courses]

    return responses.Successful(content=student_courses_response)

@students_router.get("/courses/progress")
async def get_student_courses_progress(payload: dict = Depends(get_current_user)):
    if payload.get("role") != "student":
        return responses.Forbidden(content="Only a Student user can perform this action")

    progress_data = await get_student_courses_progress_service(payload.get("id"))
    # progress_data["progress"] = str(progress_data["progress"]) + "%"
    progress_response = [CoursesProgressResponse(**prd).model_dump(mode="json") for prd in progress_data]

    return responses.Successful(content=progress_response)


@students_router.post('/avatar')
async def upload_avatar_photo(file: UploadFile = File(...), payload: dict = Depends(get_current_user) ):
    email = payload.get("email")
    # Uploading and generating URL
    url = upload_avatar(file, email)

    # Updating URL in database
    await update_avatar_url(url, email)
    student_profile = await get_student_by_email(email)

    return responses.Created(content=StudentResponse(**student_profile).model_dump(mode="json"))

@students_router.post("/subscribe")
async def subscribe_student(payload: dict = Depends(get_current_user)):
    student = await get_student_by_email(payload.get("email"))
    subscription = await subscribe(student[0])
    return responses.Created(content=SubscriptionResponse(**subscription).model_dump(mode="json"))

@students_router.post("/enroll/{course_id}")
async def enroll(course_id: int, payload: dict = Depends(get_current_user)):
    # allowed by default
    allowed = True

    # Checking if course is premium
    course = await get_course_by_id_service(course_id)
    student_id = payload.get("id")
    if course:
        if course[5] == True:
        # Check if student is subscibed
            if await is_subscribed(student_id):
                # Checking premium courses enrollment count.
                premium_enrollments_count = await count_premium_enrollments((payload.get("id")))
                if premium_enrollments_count >= 5:
                    allowed = False
                    return responses.Unauthorized(content="Student is already enrolled to 5 premium courses. First complete or cancel enrollment.")
            else: 
                allowed = False
                return responses.Forbidden(content="Course enrollment requires premium subscription!")
    else:
        allowed = False 
        return responses.BadRequest(content=f"There is no course with id {course_id}")
    

    if allowed:
        teacher_data = await get_teacher_by_id(course[6])

        # Gathering all obejects needed
        enrollment_id = await enroll_course(course_id, student_id)
        course_object = CourseResponse(**(await get_course_by_id_service(course_id)))
        student_object = StudentResponse(**payload)

        # Sending enrollment request to course owner
        await teacher_approve_enrollment(teacher_data, student_object, course_object, enrollment_id)

        return responses.Created(content=f"Enrollment created. Course teacher will be notified about your interest.")

@students_router.put("/unenroll/{course_id}")
async def unenroll(course_id: int, payload: dict = Depends(get_current_user)):
    if payload.get("role") != "student":
        return responses.Forbidden(content="Only a Student user can perform this action")

    student_id = payload.get("id")
    service_response = await unenroll_student_service(student_id, course_id)

    if service_response:
        return responses.Successful(content="Unenrollment successful.")
    else:
        return responses.Forbidden(content="You can only unenroll courses you are currently enrolled to.")

@students_router.post("/{course_id}/rate")
async def rate_course(course_id: int, rating: int, payload: dict = Depends(get_current_user)):
    role = payload.get("role")
    if role != "student":
        return responses.Forbidden(content="Only a Student user can rate a course")
    
    student_id = payload.get("id")
    course_rating = await rate_course_service(student_id, course_id, rating)

    if not course_rating:
        return responses.Forbidden("You can only rate courses you are currently enrolled to or have completed.")
    
    return responses.Successful(content="Course rating submitted.")
    
