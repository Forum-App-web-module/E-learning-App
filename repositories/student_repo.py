from data.database import update_query, insert_query, read_query
from data.models import Subscription


async def update_student_data(
        first_name: str,
        last_name: str,
        avatar_url: str,
        user_email: str,
        update_data_func = update_query
    ):
    query = """
        UPDATE v1.students 
        SET first_name = COALESCE($1, first_name),
            last_name = COALESCE($2, last_name),
            avatar_url = COALESCE($3, avatar_url)
        WHERE email = $4
        """
    student = await update_data_func(query, (first_name, last_name, avatar_url, user_email))
    return student

async def repo_get_courses_student_all(student_id, get_data_func = read_query):
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

async def repo_get_courses_progress(student_id:int, get_data_func = read_query):
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

async def repo_update_avatar_url(url: str, user_email, update_data_func = update_query): 
    query = """
        UPDATE v1.students 
        SET avatar_url = $1 
        WHERE email = $2
    """
    student_id = await update_data_func(query, (url, user_email))
    return student_id


async def repo_subscribe(student_id, subscription: Subscription, insert_data_func = insert_query):
    query = """
        INSERT INTO v1.subscriptions (student_id, expire_date) 
        VALUES ($1, $2) 
        RETURNING id
    """
    new_id = await insert_data_func(query, (student_id, subscription.expire_date))
    return new_id


async def repo_is_subscribed(student_id, get_data_func = read_query):
    query = """
        SELECT id, student_id, subscribed_at, expire_date 
        FROM v1.subscriptions 
        WHERE student_id = $1
    """
    subscription = await get_data_func(query, (student_id,))
    return subscription[0] if subscription else None

async def repo_rate_course(student_id, course_id, rating: int, insert_data_func = insert_query):
    query = """
        INSERT INTO v1.course_rating(students_id, courses_id, rating)
        VALUES ($1, $2, $3)
        ON CONFLICT (students_id, courses_id)
        DO UPDATE SET rating = EXCLUDED.rating
        RETURNING students_id, courses_id, rating
    """
    # ON CONFLICT (student_id, course_id) DO UPDATE SET rating = EXCLUDED.rating - a student can change their rating, EXCLUDED.rating is the new raiting inserted
    rating = await insert_data_func(query, (student_id, course_id, rating))
    return rating

#get all courses a student is enrolled to or has completed
async def repo_allow_rating(student_id, course_id, get_data_func = read_query):
    query = """
        SELECT 1
        FROM v1.enrollments
        WHERE student_id = $1
        AND course_id = $2
        AND (completed_at IS NOT NULL OR (completed_at is NULL and drop_out = FALSE))
    """
    result = await get_data_func(query, (student_id, course_id))
    #print(result) # allow_rating result: [<Record ?column?=1>]
    return len(result) > 0


async def repo_validate_subscription(student_id, get_data_func = read_query):
    query = """
        SELECT 1
        FROM v1.subscriptions 
        WHERE student_id = $1 AND is_active = TRUE AND expire_date > CURRENT_DATE
    """
    subscription = await get_data_func(query, (student_id,))
    return bool(subscription)

async def repo_check_enrollment(course_id: int, student_id: int, get_data_func=read_query):
    query = """
        SELECT 1
        FROM v1.enrollments
        WHERE course_id = $1 AND student_id = $2
    """
    result = await get_data_func(query, (course_id, student_id))
    return bool(result)