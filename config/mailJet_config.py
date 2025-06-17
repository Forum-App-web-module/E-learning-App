# Future development - log to a different DB or a monitoring platform
# import logging


from mailjet_rest import Client
from os import getenv
from dotenv import load_dotenv
from pydantic import EmailStr

from data.models import TeacherResponse, StudentResponse, Course, CourseResponse, Action, Action_UserRole

load_dotenv(dotenv_path=".env")

system_email = getenv("SYSTEM_EMAIL")
admin_email = getenv("ADMIN_EMAIL")
api_key = getenv("MAILJET_API_KEY")
api_secret = getenv("MAILJET_SECRET")



mailjet = Client(auth=(api_key, api_secret), version='v3.1')


async def admin_teacher_aproval(teacher_data: TeacherResponse):
    URL = "http://127.0.0.1:8000/admins/teacher/" + f"{teacher_data.id}"
    data = {
    'Messages': [
                    {
                            "From": {
                                    "Email": system_email,
                                    "Name": "System"
                            },
                            "To": [
                                    {
                                            "Email": admin_email,
                                            "Name": "Admin team"
                                    }
                            ],
                            "Subject": "New Teacher Registration Request",
                            "TextPart": "Hope you have a great day!",
                            "HTMLPart": f"""
                                        <h3>Dear Admin,</h3>
                                        <p>There is a new teacher registration waiting for your approval.</p>
                                        <p><a href="{URL}">Click here to approve the teacher</a>!</p>
                                        <br />
                                        <p>May the admin force be with you!</p>
                                        """
                    }
            ]
    }
    result = mailjet.send.create(data=data)


async def course_deprecation_email(student_emails: list[str], course_data: CourseResponse):
    if not student_emails:
        return {"status": "no_emails"}

    if not course_data.title:
        return {"status": "no_course_title"}

    data = {
        'Messages': [
            {
                "From": {
                    "Email": system_email,
                    "Name": "System"
                },
                "To": [{"Email": email}],
                "Subject": "Course deprecation",
                "HTMLPart": f"""
                    <h3>Dear student,</h3>
                    <p>Your course <strong>{course_data.title}</strong> has been deprecated.</p>
                    <p>Feel free to reach out to us if you have any questions.</p>
                    <p>Best regards,<br>E-learning team</p>
                """
            }
            for email in student_emails
        ]
    }

    try:
        response = mailjet.send.create(data=data)
        return {
            "status": "success",
            "response_status_code": response.status_code,
            "response_data": response.json() if hasattr(response, "json") else None
        }
    except Exception as e:
        # logging.exception(f"Failed to send batch course deprecation email: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }



async def teacher_verify_email(teacher_data: TeacherResponse, teacher_id):
    URL = "http://127.0.0.1:8000/teachers/email/" + f"{teacher_id}"
    data = {
    'Messages': [
                    {
                            "From": {
                                    "Email": system_email,
                                    "Name": "System"
                            },
                            "To": [
                                    {
                                            "Email": f"{teacher_data.email}",
                                            "Name": "You"
                                    }
                            ],
                            "Subject": "Email verification needed.",
                            "TextPart": "Hope you have a great day!",
                            "HTMLPart": f"""
                                        <h3>Hello,</h3>
                                        <p>Your email needs to be verified.</p>
                                        <p><a href=\"{URL}\">Click here to verify your email!</a>!</p>
                                        <br />
                                        <p>Enjoy your teaching!</p>
                                        """
                    }
            ]
    }
    result = mailjet.send.create(data=data)



async def teacher_approve_enrollment(teacher_data: TeacherResponse, student_data: StudentResponse, course: Course, enrollment_id: int):
    URL = "http://127.0.0.1:8000/teachers/enrollments/" + f"{enrollment_id}"
    data = {
    'Messages': [
                    {
                            "From": {
                                    "Email": system_email,
                                    "Name": "System"
                            },
                            "To": [
                                    {
                                            "Email": f"{teacher_data.email}",
                                            "Name": "You"
                                    }
                            ],
                            "Subject": f"New enrollment for your course: {course.title}",
                            "TextPart": "Hope you have a great day!",
                            "HTMLPart": f"""
                                        <h3>
                                                Hello, you have a new student enrolling for the course <strong>{course.title}</strong>.
                                                <br /><br />
                                                Student information:
                                                <br />
                                                First name: {student_data.first_name}<br />
                                                Last name: {student_data.last_name}
                                                <br /><br />
                                                <a href="{URL}">Click here to approve the enrollment</a>!
                                        </h3>
                                        <br />
                                        Enjoy your teaching!
                                        """
                    }
            ]
    }
    result = mailjet.send.create(data=data)
    

async def notify_user_for_account_state(action: Action, role: Action_UserRole, user_email: str):
        data = {
        'Messages': [
                        {
                                "From": {
                                        "Email": system_email,
                                        "Name": "System"
                                },
                                "To": [
                                        {
                                                "Email": f"{user_email}",
                                                "Name": "You"
                                        }
                                ],
                                "Subject": f"Your account is {action.value.upper()}D",
                                "TextPart": "Hope you have a great day!",
                                "HTMLPart": f"""
                                                <h3>Hello,</h3>
                                                <p>Your {role.value} account has been {action.value.upper()}D"</p>
                                                <br />
                                                <p>Have a nice day!</p>
                                                """
                        }
                ]
        }
        result = mailjet.send.create(data=data)

