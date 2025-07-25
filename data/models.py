from pydantic import BaseModel, Field, EmailStr, field_serializer, field_validator
from datetime import datetime, timedelta
from typing import Annotated, Literal, Optional
from enum import Enum
from fastapi import Query


# --- Enums and Type Aliases ---

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

Password = Annotated[str, Field(min_length=8, max_length=30)]
Rating = Annotated[int, Field(ge=1, le=10)]
Name = Annotated[str, Field(min_length=2, max_length=30)]

class Action(str, Enum):
    activate = "activate"
    deactivate = "deactivate"

class Action_UserRole(str, Enum):
    student = "student"
    teacher = "teacher"

# --- Login and Registration ---

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


# --- Response Models ---

class UpdateStudentRequest(BaseModel):
    first_name: Name | None
    last_name: Name | None
    avatar_url: Optional[str] | None

    @field_validator('avatar_url')
    def validate_avatar_url(cls, value):
        if value in [None, ""]:
            return None

        import re
        pattern = r"^https?:\/\/.*\.(png|jpg|jpeg)$"
        if not re.match(pattern, value):
            raise ValueError("avatar_url must be a valid URL ending with .png, .jpg, or .jpeg")
        return value


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


# --- Course Models ---

class CourseBase(BaseModel):
    title: str
    description: str
    tags: str
    picture_url: str
    is_premium: bool
    is_hidden: bool = False

class CourseCreate(CourseBase):
    owner_id: int

class CourseStudentResponse(BaseModel):
    id: int
    title: str
    description: str
    tags: str
    picture_url: str
    is_premium: bool
    created_on: datetime
    rating: Optional[float] = Field(alias="average_rating")

class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    tags: str
    picture_url: str
    is_premium: bool
    owner_id: int
    is_hidden: bool
    created_on: datetime

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

class CoursesProgressResponse(BaseModel):
    course_id: int
    title: str
    progress_percentage: float

class AdminCourseListResponse(BaseModel):
    id: int
    title: str
    description: str
    tags: str
    picture_url: str
    is_premium: bool
    owner_id: int
    student_count: int = 0
    average_rating: Optional[float]
    created_on: datetime

# --- Section Models ---

class Section(BaseModel):
    title: str
    content: str
    description: str
    is_hidden: bool = False

class SectionCreate(Section):
    pass

class SectionOut(Section):
    id: int
    course_id: int

class SectionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, example="New section title")
    content:  Optional[str] = Field(default=None, example="New content")
    description:  Optional[str] = Field(default=None, example="New section description")




# --- Event Models ---

class Event(BaseModel):
    id: int | None
    user_id: int
    event_type: str
    description: str
    timestamp: datetime = datetime.now()


# --- Subscription and Progress Models ---

class Subscription(BaseModel):
    id: int | None = None
    student_id: int
    subscribed_at: datetime = Field(default_factory=datetime.now)
    expire_date: datetime = Field(default_factory=lambda: datetime.now() + timedelta(days=365))

    @property
    def is_active(self) -> bool:
        return self.expire_date < datetime.now()
    
class SubscriptionResponse(BaseModel):
    id: int
    student_id: int
    subscribed_at: datetime
    expire_date: datetime

    @field_serializer('subscribed_at', 'expire_date')
    def format_datetime(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')

class Section_progress(BaseModel):
    id: int | None
    student_id: int
    course_id: int
    section_id: int
    is_completed: bool = True


# --- Rating and Resource Models ---

class Course_rating(BaseModel):
    id: int | None
    user_id: int
    rating_given: Rating


class External_resourse(BaseModel):
    id: int
    section_id: int
    url: str


# --- Enrollment Models ---

class Enrollment(BaseModel):
    id: int | None
    student_id: int
    course_id: int
    is_approved: bool = False
    requested_at: datetime = datetime.now()
    approved_at: datetime | None
    completed_at: datetime | None


class EnrollmentResponse(BaseModel):
    id: int | None
    student_id: int
    course_id: int
    is_approved: bool = False
    requested_at: datetime
    approved_at: datetime | None
    completed_at: datetime | None
    drop_out: bool


# e.student_id, s.email, s.first_name, s.last_name,
# e.course_id, c.title, e.requested_at, e.approved_at, e.completed_at, e.drop_out, c.created_on
class EnrollmentReport(BaseModel):
    student_id: int
    email: EmailStr
    first_name: Name | None
    last_name: Name | None
    course_id: int
    title: str
    requested_at: datetime
    approved_at: datetime | None
    completed_at: datetime | None
    drop_out: bool
    created_on: datetime

# --- Search and Filter Models ---

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class CourseSortField(str, Enum):
    title = "title"
    rating = "rating"
    created_on = "created_on"

class TeacherSortField(str, Enum):
    created_on = "created_on"
    title = "title"

class StudentSortField(str, Enum):
    approved_at = "approved_at"
    title = "title"

class CourseFilterBase(BaseModel):
    title: Optional[str] = Field(default="", description="Filter by course title")
    tag: Optional[str] = Field(default="", description="Filter by course tag")
    order: SortOrder = Field(default=SortOrder.asc, description="Sort order: asc or desc")
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)    
class CourseFilterOptions(CourseFilterBase):
    sort_by: CourseSortField = Field(default=CourseSortField.title, description="Sort by title, rating, or created_on")

class TeacherCourseFilter(CourseFilterBase):
    sort_by: TeacherSortField = Field(default=TeacherSortField.created_on, description="Sort by created_on or title")

class StudentCourseFilter(CourseFilterBase):
    sort_by: StudentSortField = Field(default=StudentSortField.approved_at, description="Sort by approved_at or title")

class AdminCourseFilterOptions(BaseModel):
    title: Optional[str] = Field(default="", description="Filter by course title")
    teacher_id: Optional[int] = Field(default=None, description="Filter by teacher ID")
    student_id: Optional[int] = Field(default=None, description="Filter by student ID")
    limit: int = Field(default=5, ge=1, le=100, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Pagination offset")




