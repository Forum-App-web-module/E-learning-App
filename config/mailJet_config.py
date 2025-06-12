



from mailjet_rest import Client
from os import getenv
from dotenv import load_dotenv
from data.models import TeacherResponse, StudentResponse, Course

load_dotenv(dotenv_path="external_keys.env")

system_email = getenv("SYSTEM_EMAIL")
api_key = getenv("MAILJET_API_KEY")
api_secret = getenv("MAILJET_SECRET")


mailjet = Client(auth=(api_key, api_secret), version='v3.1')


async def admin_teacher_aproval(teacher_data: TeacherResponse, admin_email: str):
    URL = "http://127.0.0.1:8000/admins/approve_teacher/" + f"{teacher_data.id}"
    data = {
    'Messages': [
                    {
                            "From": {
                                    "Email": "noreply@exaple.com",
                                    "Name": "System"
                            },
                            "To": [
                                    {
                                            "Email": f"{admin_email}",
                                            "Name": "Admin of Example"
                                    }
                            ],
                            "Subject": "New Teacher Registration Request",
                            "TextPart": "Hope you have a great day!",
                            "HTMLPart": f"<h3>Dear Admin, there is new teacher registration waiting your approval. <a href=\"{URL}>Click here to approve the teacher</a>!</h3><br />May the delivery force be with you!"
                    }
            ]
    }
    result = mailjet.send.create(data=data)


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
    