from fastapi import APIRouter, UploadFile, File, Body, Depends
from typing import Optional
from config.mailJet_config import teacher_approve_enrollment
from config.cloudinary_config import upload_avatar
from security.auth_dependencies import get_current_user
from fastapi.security import OAuth2PasswordBearer
from services.course_service import enroll_course, count_premium_enrollments, get_course_by_id_service
from services.enrollment_service import unenroll_student_service
from services.student_service import (
    update_avatar_url,
    get_student_by_email,
    update_student_service,
    get_student_courses_service,
    get_student_courses_progress_service,
    rate_course_service, complete_section_service,
    complete_course_service, check_enrollment_service
)
from services.teacher_service import get_teacher_by_id
from services.subscription_service import subscribe, is_subscribed
from data.models import (
    SubscriptionResponse,
    UpdateStudentRequest,
    StudentResponse,
    CourseStudentResponse,
    CoursesProgressResponse,
    TeacherResponse,
    CourseResponse, UserRole)
from common import responses

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

students_router = APIRouter(prefix="/students", tags=["students"])


@students_router.get("/profile")
async def get_profile(payload: dict = Depends(get_current_user)):
    """
    Get the authenticated student's profile information.

    Returns:
        Basic details about the logged-in student (first name, last name, avatar, etc.).
    """
    if payload.get("role") != "student":
        return responses.Forbidden(content="Only a Student user can perform this action")
    student = await get_student_by_email(payload.get("email"))
    return responses.Successful(content=StudentResponse(**student).model_dump(mode="json"))

@students_router.put("/account")
async def update_student(
        payload: dict = Depends(get_current_user),
        data: UpdateStudentRequest = Body(...)
):
    """
    Update the logged-in student's personal data.

    Request Body:
        UpdateStudentRequest: First name, last name, and/or avatar URL.

    Returns:
        The updated student profile.
    """
    if payload.get("role") != "student":
        return responses.Forbidden(content="Only a Student user can perform this action")

    student = await update_student_service(
        data.first_name,
        data.last_name,
        data.avatar_url,
        payload.get("email"),
        payload.get("role")
    )

    return responses.Successful(content=StudentResponse(**student).model_dump(mode="json"))

@students_router.get("/courses")
async def get_student_courses(payload: dict = Depends(get_current_user)):
    """
    Fetches the list of courses associated with a student user.

    The operation is accessible only to users with the "student" role. If the
    user has the required role, the courses are fetched using the service layer and
    formatted according to the response model.

    :param payload: The request payload containing user information, typically
        resolved using the dependency injection.
    :type payload: dict
    :return: A successful response containing the list of student courses if the
        user is a student, or a forbidden response if the user lacks the required role.
    :rtype: JSONResponse
    """
    if payload.get("role") != "student":
        return responses.Forbidden(content="Only a Student user can perform this action")

    student_courses = await get_student_courses_service(payload.get("id")) or []
    student_courses_response = [CourseStudentResponse(**sc).model_dump(mode="json") for sc in student_courses]

    return responses.Successful(content=student_courses_response)

@students_router.get("/courses/progress")
async def get_student_courses_progress(payload: dict = Depends(get_current_user)):
    """
    Retrieve the completion progress of each enrolled course.

    Returns:
        Course IDs, titles, and percentage progress for each course.
    """
    if payload.get("role") != "student":
        return responses.Forbidden(content="Only a Student user can perform this action")

    progress_data = await get_student_courses_progress_service(payload.get("id"))
    # progress_data["progress"] = str(progress_data["progress"]) + "%"
    progress_response = [CoursesProgressResponse(**prd).model_dump(mode="json") for prd in progress_data]

    return responses.Successful(content=progress_response)


@students_router.post('/avatar')
async def upload_avatar_photo(file: UploadFile = File(...), payload: dict = Depends(get_current_user) ):
    """
    Upload and update the student's profile avatar.

    Uploads an image to cloud storage and updates the avatar URL in the profile.

    Returns:
        The updated student profile with the new avatar URL.
    """
    email = payload.get("email")
    student_profile = await get_student_by_email(email)
    if student_profile:
        # Uploading and generating URL
        url = await upload_avatar(file, email)

        # Updating URL in database
        await update_avatar_url(url, email)
        
        if student_profile: 
            return responses.Created(content=StudentResponse(**student_profile).model_dump(mode="json"))
    return responses.BadRequest(content="Account missmatch. Please login as student and try again.")

@students_router.post("/subscribe")
async def subscribe_student(payload: dict = Depends(get_current_user)):
    """
    Subscribe the student to a premium plan.

    Triggers a mock or real payment process and updates subscription status.

    Returns:
        Subscription details (e.g., activation status, expiration).
    """
    student = await get_student_by_email(payload.get("email"))
    subscription = await subscribe(student[0])
    return responses.Created(content=SubscriptionResponse(**subscription).model_dump(mode="json"))

@students_router.post("/enroll/{course_id}")
async def enroll(course_id: int, payload: dict = Depends(get_current_user)):
    """
    Enroll the student in a specific course.

    Validates subscription status for premium courses, checks enrollment limits,
    and sends a notification to the course's teacher for approval.

    Path Parameters:
        course_id: ID of the course to enroll in.

    Returns:
        Enrollment status message.
    """
    # allowed by default
    allowed = True

    # Checking if course is premium
    course = await get_course_by_id_service(course_id)
    student_id = payload.get("id")
    if course:
        if course[5] == True:
        # Check if student is subscribed
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
    """
    Unenroll the student from a course.

    Only allowed for students currently enrolled in the given course.

    Path Parameters:
        course_id: ID of the course to leave.

    Returns:
        Confirmation message or error if unenrollment is not permitted.
    """
    if payload.get("role") != "student":
        return responses.Forbidden(content="Only a Student user can perform this action")

    student_id = payload.get("id")
    service_response = await unenroll_student_service(student_id, course_id)

    if service_response:
        return responses.Successful(content="Unenrollment successful.")
    else:
        return responses.Forbidden(content="You can only unenroll courses you are currently enrolled to.")

@students_router.post("/{course_id}/rate")
async def rate_course(course_id: int, rating: int = Body(...), payload: dict = Depends(get_current_user)):
    """
    Rate a course the student is enrolled in.

    Students may submit one rating per course, only if enrolled or completed.

    Query Parameters:
        rating: Integer rating score (e.g., 1–10).

    Returns:
        A success message if the rating is recorded.
    """
    role = payload.get("role")
    if role != "student":
        return responses.Forbidden(content="Only a Student user can rate a course")
    
    student_id = payload.get("id")
    course_rating = await rate_course_service(student_id, course_id, rating)

    if not course_rating:
        return responses.Forbidden("You can only rate courses you are currently enrolled to or have completed.")
    
    return responses.Successful(content="Course rating submitted.")
    


@students_router.post("/{course_id}/sections/{section_id}/complete")
async def complete_section(course_id: int, section_id: int, payload: dict = Depends(get_current_user)):
    """
    Mark a course section as completed.

    Accessible only to students who are enrolled in the parent course.

    Path Parameters:
        course_id: ID of the course.
        section_id: ID of the section to mark as complete.

    Returns:
        A success message indicating the section was completed.
    """
    if payload.get("role") != UserRole.STUDENT:
        return responses.Unauthorized(content="Only students can complete sections.")

    student_id = payload.get("id")
    enrolled = await check_enrollment_service(course_id, student_id)

    if not enrolled:
        return responses.Forbidden(content="You must be enrolled to complete a section.")

    await complete_section_service(student_id, section_id)
    return responses.Successful(content={"message": f"Section {section_id} marked as completed."})


@students_router.post("/{course_id}/complete")
async def complete_course(course_id: int, payload: dict = Depends(get_current_user)):
    """
    Mark the course as completed by the student.

    Allowed only if all sections in the course are completed.

    Path Parameters:
        course_id: ID of the course to mark as completed.

    Returns:
        Success message or error if the course is incomplete.
    """
    if payload.get("role") != UserRole.STUDENT:
        return responses.Unauthorized(content="Only students can complete courses.")

    student_id = payload.get("id")
    enrolled = await check_enrollment_service(course_id, student_id)

    if not enrolled:
        return responses.Forbidden(content="You must be enrolled to complete this course.")

    progress_data = await get_student_courses_progress_service(student_id)
    course_progress = next((course for course in progress_data if course["course_id"] == course_id), None)

    if not course_progress:
        return responses.NotFound(content="Course progress data not found.")

    if course_progress["progress_percentage"] < 100:
        return responses.Forbidden(content="You must complete all sections before completing the course.")

    await complete_course_service(student_id, course_id)
    return responses.Successful(content={"message": f"Course {course_id} marked as completed."})
