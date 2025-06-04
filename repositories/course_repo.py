from data.models import Course,CourseUpdate, Course_rating, SectionCreate
from data.database import insert_query, read_query, update_query, query_count
from typing import Optional

# get all public courses, display title and description onyl

async def get_all_public_courses_repo(tag: Optional[str], get_data_func = read_query):

    query= """
    SELECT title, description, tags
    FROM v1.courses
    WHERE is_premium = FALSE
    AND is_hidden = FALSE

    """
    if not tag:
        public_courses = await get_data_func(query)
    else:    
        query += "AND tags ILIKE '%' || $1 || '%';"
        #query = """
        #SELECT title, description, tags
        #FROM v1.courses
        #WHERE is_premium = FALSE
        #AND is_hidden = FALSE
        #AND tags ILIKE '%' || $1 || '%';
    #"""
    # AND tags ILIKE '%' || $1 || '%' 
    # AND tags ILIKE '%pyt%';
        public_courses = await get_data_func(query, (tag, ))

    return public_courses

# get course by id
async def read_course_by_id(id: int, get_data_func = read_query):

    query = """
    SELECT *
    FROM v1.courses
    WHERE id = $1
"""

    result = await get_data_func(query, (id, ))
    return result[0] if result else None

# get all courses per teacher
async def read_all_courses_per_teacher(teacher_id, get_data_func = read_query):

    query = """
    SELECT *
    FROM v1.courses
    WHERE owner_id = $1
"""

    courses = await get_data_func(query, (teacher_id, ))
    return courses if courses else None

# get all courses a student is enrolled to 
async def get_all_student_courses_repo(student_id, get_data_func = read_query):
    query = """
    SELECT c.id AS course_id, c.title
    FROM v1.enrollments e
    INNER JOIN v1.courses c ON e.course_id = c.id
    WHERE e.student_id = $1
"""
    courses = await get_data_func(query, (student_id, ))
    return courses if courses else None

# create course
async def insert_course(course_data: Course, insert_data_func = insert_query):

    query = """
            INSERT INTO v1.courses (title, description, tags, picture_url, is_premium, owner_id, is_hidden, created_on )
            VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            RETURNING id
"""

    values = (
        course_data.title,
        course_data.description,
        course_data.tags,
        course_data.picture_url,
        course_data.is_premium,
        course_data.owner_id,
        course_data.is_hidden,
    )
    course = await insert_data_func(query, values)
    return course
    
# update course by title
async def update_course_data(id: int, updates: CourseUpdate, update_data_func = update_query): #update_query -> int

    query = """
    UPDATE v1.courses
    SET 
        title = COALESCE($2, title),
        description = COALESCE($3, description),
        tags = COALESCE($4, tags),
        picture_url = COALESCE($5, picture_url),
        is_premium = COALESCE($6, is_premium),
        is_hidden = COALESCE($7, is_hidden)
    WHERE id = $1
    RETURNING id
"""
    data = (
        id,
        updates.title,
        updates.description,
        updates.tags,
        updates.picture_url,
        updates.is_premium,
        updates.is_hidden
    )

    updated = await update_data_func(query, data)
    return updated if updated else None

async def repo_count_premium_enrollments(student_id, count_data_func = query_count):
    query = "SELECT count(*) FROM v1.enrollments as en JOIN v1.courses as co on en.course_id=co.id WHERE is_approved = true AND completed_at IS NULL AND drop_out = false AND is_premium = true AND student_id = $1"
    enrollments = await count_data_func(query,(student_id,))
    return enrollments
