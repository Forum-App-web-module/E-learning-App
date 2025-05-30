from data.models import Course
from data.database import insert_query, read_query, update_query


# get course by id
async def read_course_by_id(id: int, get_data_func = read_query):

    query = """
    SELECT *
    FROM v1.courses
    WHERE id = $1
"""

    course = await read_query(query)
    return course

# get all courses

async def read_all_courses(get_data_func = read_query):

    query = """
    SELECT *
    FROM v1.courses
"""

    courses = await read_query(query)
    return courses

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
    course = await insert_query(query, values)
    return course
    
# update course by title

async def update_course_by_id(title: str, get_data_func = read_query):

    query = """
    SELECT *
    FROM v1.courses
    WHERE id = $1
"""

    course = await read_query(query)
    return course

# get rating

async def get_course_rating(id: int, get_data_func = read_query):
    pass