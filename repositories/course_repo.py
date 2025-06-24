from data.models import CourseUpdate, CourseFilterOptions, CourseCreate, TeacherCourseFilter, StudentCourseFilter
from data.database import insert_query, read_query, update_query, query_count
from typing import Optional

# get all public courses, display title and description only

async def get_all_courses_repo(filters: CourseFilterOptions, premium: bool, get_data_func = read_query):
    """
    Fetch all courses from the repository based on the given filter options.

    This asynchronous function retrieves a list of courses from the database
    according to specific filtering criteria, including search by title, tags,
    premium access, and sorting options. The results are paginated
    using limit and offset parameters.

    :param filters: An instance of CourseFilterOptions containing filtering and
        sorting criteria. This includes title, tags, sort_by, limit, offset,
        and order attributes.
    :type filters: CourseFilterOptions
    :param premium: A boolean indicating whether to return premium courses.
        If False, only non-premium courses will be fetched.
    :param get_data_func: A callable function for executing the database query.
        The default function is `read_query`.
    :return: A list of courses matching the specified filters.
    :rtype: list
    """

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
    """
    Fetches course details from the database using the course ID.

    This function executes a SQL query to retrieve details of a course
    specified by its unique identifier. The query is performed
    asynchronously using the provided function for data retrieval.

    :param id: The unique identifier of the course.
    :param get_data_func: An asynchronous function to execute the database query.
        Defaults to `read_query`.
    :return: A dictionary containing course details if found, otherwise `None`.
    """

    query = """
    SELECT *
    FROM v1.courses
    WHERE id = $1
    """

    result = await get_data_func(query, (id, ))
    return result[0] if result else None

# get all courses per teacher
async def get_all_courses_per_teacher_repo(teacher_id: int, filters: TeacherCourseFilter, get_data_func = read_query):
    """
    Retrieves a list of courses for a specific teacher from the repository based on the provided filters,
    along with the average rating for each course. The results can be sorted either by the course creation
    date or by the course title, as specified in the filters. The retrieval leverages a given data access
    function to execute the query.

    :param teacher_id: The unique identifier of the teacher whose courses are being retrieved.
    :type teacher_id: int
    :param filters: An instance of TeacherCourseFilter containing filtering and pagination options such as
        title keyword, sorting preference, limit, and offset.
    :type filters: TeacherCourseFilter
    :param get_data_func: An optional callable for executing the database query, with a default value set
        to `read_query`.
    :type get_data_func: Callable, optional
    :return: A list of dictionary objects representing the teacher's courses, enriched with their
        respective average ratings.
    :rtype: List[Dict[str, Any]]
    """

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

    return await get_data_func(query, (teacher_id, filters.title, filters.limit, filters.offset))

# get all courses a student is enrolled to 
async def get_all_student_courses_repo(student_id, filters: StudentCourseFilter, get_data_func = read_query):
    """
    Retrieves a list of courses for a specific student based on the provided filters
    from the repository. The courses fetched are those for which the student is
    enrolled and the enrollment has been approved.

    :param student_id: The unique identifier of the student.
    :type student_id: int
    :param filters: Filters provided to narrow down the courses. Includes sorting options,
        title filter, tag filter, limit, and offset for pagination.
    :type filters: StudentCourseFilter
    :param get_data_func: The function used to execute the database query. Defaults to `read_query`.
    :type get_data_func: Callable[[str, Tuple[Any, ...]], Awaitable[List[Dict[str, Any]]]]
    :return: A list of dictionaries representing the courses of the student along with their
        details, or None if no courses are found.
    :rtype: Optional[List[Dict[str, Any]]]
    """
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
        AND e.approved_at IS NOT NULL
    GROUP BY c.id, c.title, c.description, e.approved_at, e.completed_at
    ORDER BY {order_by}
    LIMIT $4 OFFSET $5
    """
    courses = await get_data_func(query, (student_id, filters.title, filters.tag, filters.limit, filters.offset ))
    return courses if courses else None

# create course
async def insert_course_repo(course_data: CourseCreate, insert_data_func = insert_query):
    """
    Inserts a course record into the database and returns the inserted record's ID.
    This asynchronous function utilizes a query to insert course data into the `v1.courses`
    table. The data includes details such as the title, description, tags, and more.
    The function makes use of an external insertion function to execute the query.

    :param course_data: Contains all required details for the course to be inserted
        including the course title, description, tags, picture URL, premium status,
        owner ID, and visibility status.
    :type course_data: CourseCreate
    :param insert_data_func: An optional callable function used for executing the
        insertion query. Defaults to `insert_query`.
    :type insert_data_func: Callable
    :return: The ID of the newly inserted course record.
    :rtype: Any
    """

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
    """
    Asynchronously updates course data in the repository. This function modifies the specified
    course with the provided updates using a parameterized SQL query. If the update is successful,
    the ID of the updated course is returned; otherwise, returns None.

    :param id: The unique identifier of the course to be updated.
    :type id: int
    :param updates: An instance of `CourseUpdate` containing the new data for the course. Fields
        in the course instance are updated only if they are not None.
    :type updates: CourseUpdate
    :param update_data_func: A function responsible for executing the update query. Defaults to
        `update_query` function.
    :type update_data_func: Callable[[str, Tuple], Optional[int]]
    :return: The ID of the updated course if the update is successful, otherwise None.
    :rtype: Optional[int]
    """

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
    """
    Counts the number of active premium enrollments for a given student. Premium enrollments
    are those that are approved, not completed, not marked as dropped out, and are premium
    courses.

    :param student_id: The ID of the student whose premium enrollments are to be counted.
    :type student_id: int
    :param count_data_func: An asynchronous function that executes a query and returns
        the count. Defaults to `query_count`.
    :type count_data_func: Callable[[str, tuple], Awaitable[int]]
    :return: The number of active premium enrollments for the student.
    :rtype: int
    """
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
    """
    Fetches course rating information from the database using the provided course ID and
    retrieves associated student data, such as the rating, student ID, and student email.

    :param course_id: The unique identifier of the course whose rating information
        is being retrieved.
    :type course_id: int
    :param get_data_func: The data-fetching function to execute the query. Defaults
        to the `read_query` function if not provided.
    :return: The result of the query, containing course rating details and student
        information.
    :rtype: Any
    """

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
    """
    Fetches and returns details about courses from the database based on the provided filters.

    This function constructs a SQL query to retrieve course information, applying the specified
    filters for title, teacher ID, and student enrollment. The data is paginated using the
    `limit` and `offset` parameters. Average rating and student count are calculated for
    each course, and results are ordered by the course creation date.

    :param title_filter: Filters courses by a case-insensitive partial match on their title.
    :param teacher_id: Filters courses by the ID of the teacher who owns them.
    :param student_id: Filters courses to include only those the specified student is enrolled in.
    :param limit: Limits the number of courses returned in the result set.
    :param offset: Skips the specified number of courses in the result set for pagination.
    :param get_data_func: Asynchronous function used to execute the database query.
    :return: A collection of course details matching the specified filters.
    :rtype: Any
    """
    
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
    """
    Marks a course as completed for a specific student in the enrollments database.

    This function updates the `completed_at` field of a student's course enrollment
    to the current timestamp, marking the course as completed. The update is performed
    only for enrollments where the course has not already been marked as completed.

    :param student_id: Identifier of the student whose enrollment record is to be updated.
    :type student_id: int
    :param course_id: Identifier of the course to be marked as completed.
    :type course_id: int
    :param update_data_func: A callable function to execute the SQL update query.
        Default is `update_query`.
    :type update_data_func: Callable
    :return: The result of the update operation, containing the `id` of the updated
        enrollment record.
    :rtype: Any
    """
    query = """
    UPDATE v1.enrollments
    SET completed_at = NOW()
    WHERE student_id = $1
        AND course_id = $2
        AND completed_at IS NULL
    RETURNING id
    """
    return await update_data_func(query, (student_id, course_id))