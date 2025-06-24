from data.database import insert_query, read_query, update_query
from datetime import datetime


async def create_enrollment_repo(course_id, student_id, insert_data_func = insert_query):
    """
    Creates a record in the enrollments repository by inserting the given course and student identifiers.

    :param course_id: The unique identifier of the course to enroll in.
    :type course_id: int or str
    :param student_id: The unique identifier of the student to be enrolled.
    :type student_id: int or str
    :param insert_data_func: A callable to execute the database insertion query.
                             Defaults to 'insert_query'.
                             This function must accept a query string and parameters as input.
    :type insert_data_func: Callable[[str, tuple], Awaitable[int]]
    :return: The unique identifier of the created enrollment if successful, or None otherwise.
    :rtype: Optional[int]
    """
    query = """INSERT INTO v1.enrollments (student_id, course_id) 
               VALUES ($1,$2) 
               RETURNING id"""

    enrollment_id = await insert_data_func(query, (student_id, course_id))

    return enrollment_id if enrollment_id else None
    # except UniqueViolationError:
    #     raise HTTPException(status_code=400, detail="Already enrolled in this course!")

async def confirm_enrollment_repo(enrollment_id, update_data_func = update_query):
    """
    Confirms the enrollment by updating the relevant database record. Sets the
    `is_approved` field to `True` and updates the `approved_at` timestamp for the
    specified enrollment ID.

    :param enrollment_id: Identifier of the enrollment to approve.
    :type enrollment_id: int
    :param update_data_func: A callable function that executes the database update
                             query. Defaults to the `update_query` function.
                             It should accept the query string and a tuple of
                             parameters as arguments and return the number of
                             rows affected asynchronously.
    :type update_data_func: Callable[[str, Tuple], Awaitable[int]]
    :return: The number of rows affected in the database after the update operation.
    :rtype: int
    """
    query = """UPDATE v1.enrollments 
               SET is_approved = $1, 
                   approved_at = $2 
               WHERE id = $3"""
    timestamp = datetime.now()
    row_count = await update_data_func(query, (True, timestamp, int(enrollment_id)))
    return row_count

async def get_enrollment_by_id_repo(enrollment_id, read_data_func = read_query ):
    """
    Fetches enrollment data from the repository by the provided enrollment ID.

    This function executes an asynchronous query to retrieve information about
    an enrollment based on its unique identifier. The query is performed through
    the provided `read_data_func`, which allows for flexibility in data-fetching
    strategies. If no enrollment is found for the given ID, the function returns
    `None`.

    :param enrollment_id: Unique identifier of the enrollment to be fetched.
    :type enrollment_id: str
    :param read_data_func: A callable that executes a database query. Defaults
                           to 'read_query'.
    :type read_data_func: Callable
    :return: Dictionary containing enrollment information if found, otherwise
             `None`.
    :rtype: Optional[Dict]
    """
    query = """SELECT *
               FROM v1.enrollments 
               WHERE id = $1"""
    result = await read_data_func(query, (enrollment_id,))
    return result[0] if result else None

async def get_enrollment_by_student_course_repo(student_id, course_id, read_data_func = read_query):
    """
    Retrieve a specific enrollment record for a given student and course from a repository.

    This function queries the enrollment database to find an entry corresponding
    to a specific `student_id` and `course_id`. It uses the provided asynchronous
    data reading function `read_data_func` to execute the query and obtain the result.
    If no entry matches the given identifiers, the function returns `None`.

    :param student_id: The unique identifier of the student.
    :type student_id: int
    :param course_id: The unique identifier of the course.
    :type course_id: int
    :param read_data_func: A callable function for executing database queries. Defaults to
        `read_query`. This function must support asynchronous execution and accept
        the query string and parameters as arguments.
    :type read_data_func: Callable[[str, Tuple[Any, ...]], Awaitable[List[Dict[str, Any]]]]
    :return: The enrollment identifier (id) if a matching record exists; otherwise, `None`.
    :rtype: Optional[Any]
    """
    query = """SELECT id 
               FROM v1.enrollments 
               WHERE student_id = $1 
                 AND course_id = $2"""
    result = await read_data_func(query, (student_id, course_id))
    return result[0] if result else None

async def unenroll_student_repo(enrollment_id: int, drop_out: bool, update_data_func = update_query):
    """
    Updates the enrollment record in the repository to set the drop-out status and mark
    the completion timestamp for a student. The function executes an SQL query to update
    the corresponding enrollment record with the provided data.

    :param enrollment_id: The unique ID of the student's enrollment record in the database.
    :type enrollment_id: int
    :param drop_out: A boolean value indicating whether the student has dropped out or not.
    :type drop_out: bool
    :param update_data_func: A function used to execute the query to update the enrollment
        record. Defaults to 'update_query' if not provided.
    :type update_data_func: Callable
    :return: The number of rows affected in the database as a result of the update query.
    :rtype: int
    """
    query = """UPDATE v1.enrollments
               SET drop_out = $2, 
                   completed_at = now() 
               WHERE id = $1"""

    row_count = await update_data_func(query, (enrollment_id, drop_out,))
    return row_count

async def unenroll_all_by_course_id_repo(course_id, update_data_func = update_query):
    """
    Updates all enrollments for a specific course to mark them as dropped out and sets the
    completion timestamp to the current time.

    :param course_id: Unique identifier of the course whose enrollments are to be updated.
    :type course_id: str
    :param update_data_func: Function used to execute the update query. This function must
        accept the query string and its respective parameters as arguments.
    :type update_data_func: Callable[[str, Tuple[bool, str]], Awaitable[int]]
    :return: Number of rows affected by the update operation.
    :rtype: int
    """
    query = """UPDATE v1.enrollments
               SET drop_out = $1, 
                   completed_at = now() 
               WHERE course_id = $2"""

    row_count = await update_data_func(query, (True, course_id,))
    return row_count