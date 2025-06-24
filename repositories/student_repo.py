from data.database import update_query, insert_query, read_query
from data.models import Subscription


async def update_student_data_repo(
        first_name: str,
        last_name: str,
        avatar_url: str,
        user_email: str,
        update_data_func = update_query
    ):
    """
    Asynchronously updates the data of a student in the repository. This function
    executes an SQL update query to modify a student's record using the specified
    parameters. Only the fields provided with values other than None will be updated,
    thanks to the use of the COALESCE function. The function uses an external
    query execution utility, provided as update_data_func, to interact with the database.

    :param first_name: The student's new first name. If set to None, the field won't be updated.
    :param last_name: The student's new last name. If set to None, the field won't be updated.
    :param avatar_url: The URL of the student's new avatar. If set to None, the field won't be updated.
    :param user_email: The email of the student whose data is to be updated. This is used to locate the record.
    :param update_data_func: A callable that executes the provided query with the corresponding parameters. Defaults to update_query.
    :return: The result of the database update operation, typically representing the updated student record.
    """
    query = """
        UPDATE v1.students 
        SET first_name = COALESCE($1, first_name),
            last_name = COALESCE($2, last_name),
            avatar_url = COALESCE($3, avatar_url)
        WHERE email = $4
        """
    student = await update_data_func(query, (first_name, last_name, avatar_url, user_email))
    return student

async def get_courses_student_all_repo(student_id, get_data_func = read_query):
    """
    Fetches all courses data for a specified student. Includes information about all free courses
    and premium courses for which the student is approved as an enrolled participant and has
    not yet completed.

    This function retrieves the courses' data including the average ratings of each course,
    calculating them by aggregating data from a course rating table. It supports asynchronous
    processing and uses parameterized queries for safe database interaction.

    :param student_id: The unique identifier of the student.
        Used to filter courses based on the enrollment and completion status.
    :type student_id: int
    :param get_data_func: An asynchronous function to execute the database
        query with the provided SQL and parameter(s). Defaults to `read_query`.
    :type get_data_func: Callable[[str, Tuple], Coroutine]
    :return: A list of dictionaries containing course data along with the average
        rating. Returns None if no courses were found.
    :rtype: Optional[List[Dict]]
    """
    query = """
        SELECT c.*, avg(cr.rating) AS average_rating FROM v1.courses c
        LEFT JOIN v1.course_rating cr ON c.id = cr.courses_id
        WHERE is_premium = FALSE
        OR (is_premium = TRUE
            AND
            id IN (SELECT e.course_id FROM v1.enrollments e
                    WHERE e.student_id = $1
                    AND e.is_approved = TRUE
                    AND e.completed_at IS NULL)
                )
        GROUP BY c.id, c.title, c.description, c.tags, c.picture_url, c.is_premium, c.created_on
    """
    courses = await get_data_func(query, (student_id, ))
    return courses if courses else None

async def get_courses_progress_repo(student_id:int, get_data_func = read_query):
    """
    Fetches the progress of courses for a specific student from the database.

    This function retrieves the progress of all courses that a student is enrolled in.
    The progress is calculated as the percentage of the course sections completed by
    the student out of the total number of course sections available in each course.

    :param student_id: Unique identifier of the student whose course progress is to
        be fetched.
    :type student_id: int
    :param get_data_func: A callable query execution function that takes an SQL
        query string and its parameters. Defaults to `read_query`.
    :type get_data_func: Callable
    :return: A list of dictionaries containing course progress information, where
        each dictionary represents a course and includes `course_id`, `title`, and
        `progress_percentage`. Returns `None` if no courses are found.
    :rtype: Optional[List[Dict[str, Any]]]
    """
    query = """
        SELECT
        c.id AS course_id,
        c.title,
        COALESCE(visited.count * 100.0 / total.count, 0) AS progress_percentage
        FROM
            v1.courses c
        LEFT JOIN (
            SELECT course_id, COUNT(*) AS count
            FROM v1.course_sections
            GROUP BY course_id
        ) total ON total.course_id = c.id
        LEFT JOIN (
            SELECT cs.course_id, COUNT(*) AS count
            FROM v1.students_course_sections scs
            JOIN v1.course_sections cs ON cs.id = scs.course_sections_id
            WHERE scs.students_id = $1 AND scs.is_completed = true
            GROUP BY cs.course_id
        ) visited ON visited.course_id = c.id
    """
    courses = await get_data_func(query, (student_id,))
    return courses if courses else None

async def update_avatar_url_repo(url: str, user_email, update_data_func = update_query):
    """
    Updates the avatar URL for a specific student, identified by their email
    address, in the `v1.students` database table. This function executes an
    SQL `UPDATE` query to modify the `avatar_url` field in the respective
    student record.

    :param url: The new avatar URL to be stored in the database.
    :param user_email: The email address of the student whose avatar URL is to
        be updated.
    :param update_data_func: A callable function responsible for executing the
        database update query. By default, it utilizes `update_query`.
    :return: The `student_id` of the updated student record.
    """
    query = """
        UPDATE v1.students 
        SET avatar_url = $1 
        WHERE email = $2
    """
    student_id = await update_data_func(query, (url, user_email))
    return student_id


async def subscribe_repo(student_id, subscription: Subscription, insert_data_func = insert_query):
    """
    Subscribes a student to a repository by inserting subscription details into the
    database and returning the created subscription ID.

    This function performs an insert operation in the database to add a new subscription
    record. It utilizes a provided callable to execute the database insertion query
    asynchronously and then retrieves the ID of the newly added record.

    :param student_id: Identifier of the student to associate with the subscription.
    :type student_id: int
    :param subscription: An instance of Subscription containing the details of the
        subscription, specifically the expiration date.
    :param insert_data_func: Callable responsible for executing the insert query into
        the database. Defaults to the `insert_query` function.
    :type insert_data_func: Callable[[str, tuple], Coroutine[Any, Any, Any]]
    :return: The unique identifier (ID) of the newly created subscription record.
    :rtype: int
    """
    query = """
        INSERT INTO v1.subscriptions (student_id, expire_date) 
        VALUES ($1, $2) 
        RETURNING id
    """
    new_id = await insert_data_func(query, (student_id, subscription.expire_date))
    return new_id


async def is_subscribed_repo(student_id, get_data_func = read_query):
    """
    Determines whether a student is subscribed to the repository by checking if a
    subscription record exists for the given student ID.

    :param student_id: The unique identifier of the student to check subscription
        status for.
    :type student_id: int
    :param get_data_func: A callable function used to execute the database query.
        Defaults to `read_query`.
    :type get_data_func: Callable

    :return: The subscription record for the given student ID if a subscription
        exists. If no subscription is found, returns None.
    :rtype: Optional[Dict]

    """
    query = """
        SELECT id, student_id, subscribed_at, expire_date 
        FROM v1.subscriptions 
        WHERE student_id = $1
    """
    subscription = await get_data_func(query, (student_id,))
    return subscription[0] if subscription else None

async def rate_course_repo(student_id, course_id, rating: int, insert_data_func = insert_query):
    """
    Asynchronously inserts or updates a course rating for a specific student. If a rating already exists for the given
    student and course, it updates the existing rating. Otherwise, it inserts a new rating. The functionality leverages
    the provided `insert_data_func` to execute database operations.

    :param student_id: The unique identifier for the student.
    :param course_id: The unique identifier for the course.
    :param rating: The rating value provided by the student for the course.
    :param insert_data_func: A callable function responsible for executing the database query. Defaults to `insert_query`.
    :return: The inserted or updated rating record as returned by the database.
    """
    query = """
        INSERT INTO v1.course_rating(students_id, courses_id, rating)
        VALUES ($1, $2, $3)
        ON CONFLICT (students_id, courses_id)
        DO UPDATE SET rating = EXCLUDED.rating
        RETURNING students_id, courses_id, rating
    """
    rating = await insert_data_func(query, (student_id, course_id, rating))
    return rating

#get all courses a student is enrolled to or has completed
async def allow_rating_repo(student_id, course_id, get_data_func = read_query):
    """
    Determines if a student is eligible to rate a course. A student is eligible if they are
    either marked as completed or haven't dropped out of the course.

    :param student_id: The unique identifier for the student
    :type student_id: int
    :param course_id: The unique identifier for the course
    :type course_id: int
    :param get_data_func: Function to execute the database query, defaults to `read_query`.
                          Should accept a SQL query string and parameters as arguments and
                          return query results.
    :type get_data_func: Callable[[str, tuple], Awaitable[list]]
    :return: True if the student is eligible to rate the course, False otherwise
    :rtype: bool
    """
    query = """
        SELECT 1
        FROM v1.enrollments
        WHERE student_id = $1
        AND course_id = $2
        AND (completed_at IS NOT NULL OR (completed_at is NULL and drop_out = FALSE))
    """
    result = await get_data_func(query, (student_id, course_id))
    return len(result) > 0


async def validate_subscription_repo(student_id, get_data_func = read_query):
    """
    Validates if a student has an active subscription. The function checks for an
    active and non-expired subscription for the specified student by querying the
    database.

    :param student_id: Unique identifier of the student.
    :type student_id: int
    :param get_data_func: Function to execute the query. Defaults to read_query.
    :type get_data_func: Callable[[str, Tuple[Any, ...]], Awaitable[Any]]
    :return: Boolean value indicating whether the student has an active
        subscription.
    :rtype: bool
    """
    query = """
        SELECT 1
        FROM v1.subscriptions 
        WHERE student_id = $1 AND is_active = TRUE AND expire_date > CURRENT_DATE
    """
    subscription = await get_data_func(query, (student_id,))
    return bool(subscription)

async def check_enrollment_repo(course_id: int, student_id: int, get_data_func=read_query):
    """
    Check if a student is enrolled in a specific course.

    This function queries the database to determine if a specific student is
    enrolled in the provided course by making use of a passed data retrieval
    function.

    :param course_id: The unique identifier of the course
    :type course_id: int
    :param student_id: The unique identifier of the student
    :type student_id: int
    :param get_data_func: Asynchronous callable used to execute the database query
        with parameters. Defaults to `read_query`.
    :type get_data_func: Callable[[str, tuple], Awaitable[Any]]
    :return: A boolean value indicating whether the student is enrolled in the
        course (True) or not (False)
    :rtype: bool
    """
    query = """
        SELECT 1
        FROM v1.enrollments
        WHERE course_id = $1 AND student_id = $2
    """
    result = await get_data_func(query, (course_id, student_id))
    return bool(result)


