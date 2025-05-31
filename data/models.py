from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timedelta
from typing import Annotated, Literal, Optional
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

Password = Annotated[str, Field(min_length=8, max_length=30)]
Rating = Annotated[int, Field(ge=1, le=10)]
Name = Annotated[str, Field(min_length=2, max_length=30)]

class LoginData(BaseModel):
    email: EmailStr
    password: Password

class RegisterData(BaseModel):
    email: EmailStr
    password: Password

class StudentRegisterData(RegisterData):
    pass

class TeacherRegisterData(RegisterData):
    mobile: str
    linked_in_url: str


class StudentResponse(BaseModel):
    email: EmailStr
    first_name: Name | None
    last_name: Name | None
    avatar_url: str | None
    is_active: bool
    notifications: bool


class TeacherResponse(BaseModel):
    id: int
    email: EmailStr
    mobile: str
    linked_in_url: str

class Admin(BaseModel):
    account_verified: bool = False

class CourseBase(BaseModel):
    title: str
    description: str
    tags: str
    picture_url: str
    is_premium: bool
    is_hidden: bool = False


class Section(BaseModel):
    title: str
    content: str
    description: str

class SectionCreate(Section):
    pass

class SectionOut(Section):
    id: int
    course_id: int

class Event(BaseModel):
    id: int | None
    user_id: int
    event_type: str
    description: str
    timestamp: datetime = datetime.now()

class Subscription(BaseModel):
    id: int | None
    student_id: int
    subscribed_at: datetime = datetime.now()
    expire_date: datetime = subscribed_at + timedelta(days=365)
    
    @property
    def is_active(self) -> bool:
        return self.expire_date < datetime.now()

class Course_rating(BaseModel):
    id: int | None
    user_id: int
    rating_given: Rating


class External_resourse(BaseModel):
    id: int
    section_id: int
    url: str

class Enrollment(BaseModel):
    id: int | None
    student_id: int
    course_id: int
    is_approved: bool = False
    requested_at: datetime = datetime.now()
    approved_at: datetime | None
    completed_at: datetime | None

class Section_progress(BaseModel):
    id: int | None
    student_id: int
    course_id: int
    section_id: int
    is_completed: bool = True

class CourseCreate(CourseBase):
    owner_id: int

class Course(CourseBase):
    id: int
    owner_id: int
    created_on: datetime = datetime.now()

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, example="New course title")
    description:  Optional[str] = Field(default=None, example="New course description")
    tags:  Optional[str] = Field(default=None, example="New Tag")
    picture_url:  Optional[str] = Field(default=None, example="New-URL")
    is_premium:  Optional[bool] = Field(default=None, example="False")
    is_hidden:  Optional[bool] = Field(default=None, example="False")


