from fastapi import APIRouter
from fastapi.params import Depends, Body
from data.models import TeacherResponse, EnrollmentReport
from security.auth_dependencies import get_current_user
from services.teacher_service import (
    get_teacher_by_email,
    update_teacher_service,
    get_enrolled_students,
    deactivate_course_service, 
    confirm_enrollment,
    verify_email,
)
from services.enrollment_service import get_enrollment_by_id
from common import responses
from router_helper import router_helper

teachers_router = APIRouter(prefix="/teachers", tags=["teachers"])

# Teachers must be able to view their account information
@teachers_router.get("/profile")
async def get_profile(payload: dict = Depends(get_current_user)):
    """
    Get the profile of the authenticated teacher.

    Returns the full teacher profile data based on their token.
    """
    teacher = await get_teacher_by_email(payload["email"])
    if teacher:
        return responses.Successful(content=TeacherResponse(**teacher).model_dump(mode="json"))
    else:
        return responses.Forbidden(content="Only a Teacher user can perform this action")



# Verify email by email. Teacher get email from system to verify his email by clicking on the Url.
@teachers_router.put("/email/{id}")
async def verify_teacher_email(id=id, payload: dict = Depends(get_current_user)):
    """
    Verify teacher's email address via URL.

    The verification link is sent by the system after registration.
    Only the owner of the account can verify.
    """
    if id == str(payload["id"]):
        await verify_email(payload["id"])
        return responses.Successful(content="Email is now verified!")
    else: return responses.Forbidden(content="Not authorised for this action.")

# Teacher gets email from system for course enrollments. This endpoint is sent to the teacher in the message.
# By clicking to the Url teacher gets this endpoint and approves.
@teachers_router.put("/enrollments/{id}")
async def approve_enrollment(id=id, payload: dict = Depends(get_current_user)):
    """
    Approve a student enrollment request.

    Triggered via a link sent to the course owner.
    Only course owners can approve enrollments.
    """

    enrollment_object = await get_enrollment_by_id(id)
    if enrollment_object:
        if await router_helper.verify_course_owner(enrollment_object.course_id, payload["id"]) == True:
            await confirm_enrollment(id)
            return responses.Successful(content="Enrollment is approved successfully.")
        return responses.Forbidden(content="Only owner can approve enrollment.")
    else: return responses.NotFound(content=f"There is no enrollment with ID: {id}")

# Teachers must be able to edit their account information
@teachers_router.put("/account")
async def update_teacher(
        payload: dict = Depends(get_current_user),
        mobile: str = Body(min_length=9, max_length=10),
        linked_in_url: str = Body(pattern=r"^https?:\/\/www\.linkedin\.com\/.+"),
):
    """
    Update teacher profile details.

    Allows teachers to update their mobile number and LinkedIn profile link.
    """
    email = payload["email"]
    if not await get_teacher_by_email(email):
            return responses.NotFound(content="You need to be Teacher for this action.")
    
    teacher = await update_teacher_service(mobile, linked_in_url, email)

    return responses.Successful(content=TeacherResponse(**teacher).model_dump(mode="json"))


# Teachers should be able to generate reports for the past and current students that have subscribed for their courses.
@teachers_router.get("/enrollment/report")
async def generate_report(payload: dict = Depends(get_current_user)):
    """
    Generate a report of students enrolled in the teacher’s courses.

    Returns historical and current enrollments.
    """
    if not await get_teacher_by_email(payload["email"]):
            return responses.NotFound(content="You need to be Teacher for this action.")

    repo_records = await get_enrolled_students(payload["id"])
    report_list = [EnrollmentReport(**r).model_dump(mode="json") for r in repo_records]

    return responses.Successful(content=report_list)

# Teachers to deactivate only courses to which they are owners when there are no student enrollments
# The SQL query checks for enrollments and updates at the same time.
@teachers_router.put("/deactivate/course/{id}")
async def deactivate_course(id: int, payload: dict = Depends(get_current_user)):
    """
    Deactivate a course owned by the teacher.

    Only allowed if the course has no enrolled students.
    """
    if not await get_teacher_by_email(payload["email"]):
            return responses.NotFound(content="You need to be Teacher for this action.")

    repo_response = await deactivate_course_service(payload["id"], int(id))

    if repo_response:
        return responses.Successful(content="Courses deactivated successfully.")
    else:
        return responses.BadRequest(content="You can deactivate only own courses where there are no students subscribed")

