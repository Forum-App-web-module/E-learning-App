from data.database import read_query, update_query

async def update_teacher_repo(mobile, linked_in_url, email, update_data_func = update_query):
    """
    Update a teacher's information in the database based on the email provided. If a value is not provided
    for a specific parameter, the existing value will remain unchanged. This function executes an asynchronous
    update query using the provided `update_data_func`.

    :param mobile: The new mobile number to update or None to retain the old value
    :param linked_in_url: The new LinkedIn URL to update or None to retain the old value
    :param email: The email associated with the teacher whose data is to be updated
    :param update_data_func: Function used to execute the update query, defaults to `update_query`
    :return: The result of the query execution or None if the query does not return any result
    """
    query = """
        UPDATE v1.teachers
        SET mobile = COALESCE($1, mobile),
            linked_in_url = COALESCE($2, linked_in_url)
        WHERE email = $3
    """

    result = await update_data_func(query, (mobile, linked_in_url, email))
    return result if result else None

async def report_enrolled_students_repo(owner_id: int,  get_data_func = read_query):
    """
    Retrieve a detailed report of enrolled students for a specific course owner.

    The function executes a query to fetch enrollment records associated with
    a specific owner ID and returns detailed information about the enrolled
    students, their courses, and statuses.

    :param owner_id: The ID of the course owner whose enrollment report
        should be fetched.
    :type owner_id: int
    :param get_data_func: An asynchronous callable that executes the query.
        By default, it uses the `read_query` function.
    :return: A list containing the enrollment report data, or None if
        no data is found.
    :rtype: list | None
    """
    query = """
        SELECT e.student_id, s.email, s.first_name, s.last_name,
           e.course_id, c.title, e.requested_at, e.approved_at, e.completed_at, e.drop_out, c.created_on
        FROM v1.enrollments AS e
            JOIN v1.courses AS c
        ON e.course_id = c.id
            JOIN v1.students AS s
        ON e.student_id = s.id
        WHERE c.owner_id = $1
    """

    report = await get_data_func(query, (owner_id, ))
    return report if report else None

async def deactivate_course_repo(teacher_id: int, course_id: int, update_data_func = update_query):
    """
    Deactivates a course by marking it as hidden in the database. The course can only be deactivated
    if it does not have any existing enrollments. The function updates the course's status and
    returns the course ID if the operation is successful. If the course cannot be deactivated,
    the function returns None.

    :param teacher_id: The ID of the teacher who owns the course.
    :type teacher_id: int
    :param course_id: The ID of the course to be deactivated.
    :type course_id: int
    :param update_data_func: An optional asynchronous function for executing the update query. Defaults to ``update_query``.
    :type update_data_func: Callable
    :return: The ID of the deactivated course if successful, otherwise None.
    :rtype: Optional[Any]
    """
    query = """
        UPDATE v1.courses c
        SET is_hidden = true
        WHERE owner_id = $1
        AND id = $2
        AND NOT EXISTS (
            SELECT 1
            FROM v1.enrollments e
            WHERE e.course_id = c.id
        )
        RETURNING c.id
    """

    result = await update_data_func(query, (teacher_id, course_id))
    return result if result else None

async def verify_email_repo(teacher_id, update_data_func = update_query):
    """
    Verifies the email of a teacher in the database by updating the
    email_verified status to True. The function executes an update query
    through the provided update_data_func and returns the query result.

    :param teacher_id: Unique identifier of the teacher whose email is
        to be verified.
    :type teacher_id: Any
    :param update_data_func: A callable function that executes the database
        update query. Defaults to `update_query` if not provided.
    :type update_data_func: Callable
    :return: The result of the update query execution.
    :rtype: Any
    """
    query = "UPDATE v1.teachers SET email_verified = $1 WHERE id = $2"
    result = await update_data_func(query, (True, teacher_id))
    return result

async def validate_teacher_verified_and_activated_repo(teacher_id, get_data_func = read_query):
    """
    Validates whether a teacher is both email verified and active in the repository.

    This function attempts to retrieve a specific teacher's information from the
    repository based on their `teacher_id`. It verifies that the teacher's email
    is marked as verified and that the teacher's status is active.

    :param teacher_id: Unique identifier of the teacher being verified.
    :param get_data_func: Function to execute database queries. Defaults to
                          the `read_query` function if not provided.
    :return: An asynchronous result representing the requested teacher data,
             or an empty result if no match is found.
    """
    query = "SELECT * FROM v1.teachers WHERE id = $1 and email_verified = $2 and is_active = $3"
    result = await get_data_func(query,(teacher_id, True, True))
    return result