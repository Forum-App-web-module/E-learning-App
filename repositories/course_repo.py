from data.models import CourseUpdate, CourseFilterOptions, CourseCreate, TeacherCourseFilter, StudentCourseFilter
from data.database import insert_query, read_query, update_query, query_count
from typing import Optional

# get all public courses, display title and description onyl

async def get_all_courses_repo(filters: CourseFilterOptions, premium: bool, get_data_func = read_query):

    sort_fields = {"title":"c.title", "created_on":"c.created_on", "rating":"average_rating"}
    sort_by_field = sort_fields.get(filters.sort_by, "c.title")
    order_by = "desc" if filters.order.lower() == "desc" else "asc"

    premium_clause = "" if premium else "AND c.is_premium = FALSE"

    query= f"""
    SELECT c.id, c.title, c.description, c.tags, c.picture_url, c.created_on, ROUND(AVG(cr.rating), 1) AS average_rating
    FROM v1.courses c
    LEFT JOIN v1.course_rating cr ON c.id = cr.courses_id
    WHERE c.is_hidden = FALSE
        {premium_clause}
        AND c.is_premium = FALSE
        AND (c.title ILIKE '%' || $1 || '%' OR $1 = ' ')
        AND (c.tags ILIKE '%' || $2 || '%' OR $2 = ' ')
    GROUP BY c.id, c.title, c.description, c.tags, c.picture_url, c.created_on
    ORDER BY {sort_by_field} {order_by}
    LIMIT $3 OFFSET $4
    """
    params = (filters.title, filters.tag, filters.limit, filters.offset)

    return await get_data_func(query, params)

# get course by id
async def get_course_by_id_repo(id: int, get_data_func = read_query):

    query = """
    SELECT *
    FROM v1.courses
    WHERE id = $1
    """

    result = await get_data_func(query, (id, ))
    return result[0] if result else None

# get all courses per teacher
async def get_all_courses_per_teacher_repo(teacher_id: int, filters: TeacherCourseFilter, get_data_func = read_query):

    order_by = "c.created_on" if filters.sort_by == "created_on" else "c.title"

    query =f"""
    SELECT c.*,
    ROUND(AVG(cr.rating), 1) as average_rating
    FROM v1.courses c
    LEFT JOIN v1.course_rating cr ON c.id = cr.courses_id
    WHERE owner_id = $1 AND c.title ILIKE '%' || $2 || '%'
    GROUP BY c.id
    ORDER by {order_by}
    LIMIT $3 OFFSET $4
    """

    courses = await get_data_func(query, (teacher_id, filters.title, filters.limit, filters.offset))
    return courses if courses else None

# get all courses a student is enrolled to 
async def get_all_student_courses_repo(student_id, filters: StudentCourseFilter, get_data_func = read_query):
    order_by = "e.approved_at" if filters.sort_by == "approved_at" else "c.title"
    query = f"""
    SELECT c.id, c.title,c.description, e.approved_at, e.completed_at,
    ROUND(AVG(cr.rating), 1) AS average_rating 
    FROM v1.enrollments e
    INNER JOIN v1.courses c ON e.course_id = c.id
    LEFT JOIN v1.course_rating cr ON c.id = cr.courses_id
    WHERE e.student_id = $1
        AND c.title ILIKE '%' || $2 || '%'
        AND c.tags ILIKE '%' || $3 || '%'
    GROUP BY c.id, c.title, c.description, e.approved_at, e.completed_at
    ORDER BY {order_by}
    LIMIT $4 OFFSET $5
    """
    courses = await get_data_func(query, (student_id, filters.title, filters.tag, filters.limit, filters.offset ))
    return courses if courses else None

# create course
async def insert_course_repo(course_data: CourseCreate, insert_data_func = insert_query):

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
async def update_course_data_repo(id: int, updates: CourseUpdate, update_data_func = update_query): #update_query -> int

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

async def count_premium_enrollments_repo(student_id, count_data_func = query_count):
    query = """
    SELECT count(*) 
    FROM v1.enrollments as en 
    JOIN v1.courses as co on en.course_id=co.id 
    WHERE is_approved = true 
        AND completed_at IS NULL 
        AND drop_out = false 
        AND is_premium = true 
        AND student_id = $1
        """
    enrollments = await count_data_func(query,(student_id,))
    return enrollments

async def get_course_rating_repo(course_id: int, get_data_func = read_query):

    query = """
    SELECT cr.rating, cr.students_id, s.email
    FROM v1.course_rating cr
    JOIN v1.students s ON cr.students_id = s.id
    WHERE cr.courses_id = $1

    """

    return await get_data_func(query, (course_id,))

async def admin_course_view_repo(
        title_filter: str,
        teacher_id: Optional[int],
        student_id: Optional[int],
        limit: int,
        offset: int,
        get_data_func = read_query
        ):
    
    query = f"""
    SELECT
        c.id, c.title, c.is_premium, c.description, c.tags, c.picture_url, c.owner_id, c.created_on,
        COUNT(DISTINCT e.id) AS students_count,
        ROUND(AVG(cr.rating), 1) AS average_rating
    FROM v1.courses c
    LEFT JOIN v1.enrollments e ON c.id = e.course_id
    LEFT JOIN v1.course_rating cr ON c.id = cr.courses_id
    WHERE c.is_hidden = FALSE
        AND (c.title ILIKE '%' || $1 || '%' OR $1 = '' ) 
        AND ($2::INT IS NULL OR c.owner_id = $2)
        AND ($3::INT IS NULL OR EXISTS (
            SELECT 1 FROM v1.enrollments e2 WHERE e2.course_id = c.id AND e2.student_id = $3
        ))
    GROUP BY c.id
    ORDER BY c.created_on DESC
    LIMIT $4 OFFSET $5
    """

    return await get_data_func(query, (title_filter, teacher_id, student_id, limit, offset))

async def complete_course_repo(student_id: int, course_id: int, update_data_func = update_query):
    query = """
    UPDATE v1.enrollments
    SET completed_at = NOW()
    WHERE student_id = $1
        AND course_id = $2
        AND completed_at IS NULL
    RETURNING id
    """
    return await update_data_func(query, (student_id, course_id))