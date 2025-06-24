from data.models import SectionCreate, SectionUpdate, UserRole
from data.database import insert_query, update_query, read_query

async def insert_section_repo(course_id: int, section: SectionCreate, insert_data_func = insert_query):
    """
    Inserts a new section into the course_sections table in the database and returns the ID of the newly created
    section. This function allows dynamic injection of a query execution function to facilitate database
    interfacing for testing or other purposes. It expects input arguments that describe the course section to
    be added to the specific course ID.

    :param course_id: The unique identifier of the course to which the section belongs.
    :type course_id: int
    :param section: An object containing details about the section, including title, content, description,
        and visibility.
    :type section: SectionCreate
    :param insert_data_func: The function used to execute the database query for inserting data. Defaults to
        the insert_query function if not provided.
    :return: The ID of the newly inserted section if the operation is successful, otherwise None.
    :rtype: Optional[int]
    """
    query = """
        INSERT INTO v1.course_sections (title, course_id, content, description, is_hidden)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    """

    data = (
        section.title,
        course_id,
        section.content,
        section.description,
        section.is_hidden
    )

    result  = await insert_data_func(query, data)
    return result if result else None

async def update_section_repo(id: int, updates: SectionUpdate, update_data_func = update_query):
    """
    Asynchronously updates a section in the course sections repository. The updated
    fields are determined based on the provided `updates` parameter. If a field in
    `updates` is `None`, it will retain its current value in the database.

    :param id: Identifier of the section to be updated.
    :type id: int
    :param updates: Object containing the updated values for the section's fields.
    :type updates: SectionUpdate
    :param update_data_func: Function used to execute the update query. Defaults
        to `update_query` if not provided.
    :return: The identifier of the updated section if successful, otherwise `None`.
    :rtype: Optional[int]
    """
    query = """
    UPDATE v1.course_sections
    SET
        title = COALESCE($2, title),
        content = COALESCE($3, content),
        description = COALESCE($4, description)
    WHERE id = $1
    RETURNING id

    """

    data = (
        id,
        updates.title,
        updates.content,
        updates.description
    )

    updated = await update_data_func(query, data)
    return updated if updated else None

async def hide_section_repo(id: int, update_data_func = update_query):
    """
    Updates a course section to be hidden based on its unique identifier. This function interacts
    with the database to set the `is_hidden` flag to `TRUE` for the specified section ID. The
    operation uses a parameterized query to prevent SQL injection. An optional update function
    can be provided for customized database interaction.

    :param id: The unique identifier of the course section to be hidden.
    :type id: int
    :param update_data_func: The function to execute the update query in the database. It must
        accept a query string and parameters and return the result of the query execution.
    :type update_data_func: Callable
    :return: The unique identifier of the hidden course section as returned from the database.
    :rtype: int
    """
    query = """
    UPDATE v1.course_sections
    SET is_hidden = TRUE
    WHERE id = $1
    RETURNING id
    """
    return await update_data_func(query, (id, ))

async def get_all_course_sections_repo(
        course_id: int,
        sort_by: str = "id",
        order: str = "asc",
        role: UserRole = UserRole.STUDENT,
        user_id: int | None = None,
        owner_id: int | None = None,
        get_data_func = read_query
        ):
    """
    Fetches all course sections based on provided criteria and user permissions.

    This asynchronous function retrieves course sections from the database, employing
    various filtration and sorting mechanisms. It enforces access control ensuring that
    only authorized users are allowed to access certain data. By default, sections are
    sorted by their ID in ascending order. Admins and teachers (if they own the course)
    can see all sections, while others can only view visible sections.

    :param course_id: The unique identifier of the course whose sections are to be retrieved.
    :type course_id: int
    :param sort_by: Criterion to sort the sections by; defaults to "id". Accepted values are
        "id", "title".
    :type sort_by: str
    :param order: Order in which to sort the results; defaults to "asc". Accepted values are
        "asc" for ascending and "desc" for descending.
    :type order: str
    :param role: User role specifying the level of access (e.g., admin, teacher, or student).
        Defaults to `UserRole.STUDENT`.
    :type role: UserRole
    :param user_id: (Optional) ID of the user requesting the data. Used to check access permissions.
    :type user_id: int | None
    :param owner_id: (Optional) ID of the course owner. Determines if the requesting user is
        the course owner when their role is a teacher.
    :type owner_id: int | None
    :param get_data_func: Function to execute the query, which defaults to `read_query`.
        This function is responsible for fetching data from the database.
    :type get_data_func: Callable
    :return: A list of course sections if any exist and the user has permission. Returns
        None if no sections are found or accessible based on the criteria.
    :rtype: list | None
    """
    
    sorting_options = {"id", "title"}
    order_options = {"asc","desc"}

    if sort_by not in sorting_options:
        sort_by = "id"

    if order not in order_options:
        order = "asc"

    if role == UserRole.ADMIN or (role == UserRole.TEACHER and user_id == owner_id):
        
        query = f"""
        SELECT * FROM v1.course_sections
        WHERE course_id = $1
        ORDER BY {sort_by} {order}
    """       
        params = (course_id, )
    else:
        query = f"""
        SELECT * FROM v1.course_sections
        WHERE course_id = $1 AND is_hidden = FALSE
        ORDER BY {sort_by} {order}
    """
        params = (course_id, )

    all_sections = await get_data_func(query, params)
    return all_sections if all_sections else None

async def complete_section_repo(student_id: int, section_id: int, insert_data_func = insert_query):
    """
    Asynchronously marks a specific course section as completed for a student by updating
    or inserting the data into the database. If the record already exists, it updates
    the `is_completed` flag to TRUE.

    :param student_id: ID of the student who completed the course section
    :type student_id: int
    :param section_id: ID of the course section to be marked as completed
    :type section_id: int
    :param insert_data_func: A callable function used for executing the database insert query.
                             Defaults to `insert_query`.
    :type insert_data_func: Callable[[str, tuple], Awaitable[Any]]
    :return: Result of the database operation performed by `insert_data_func`.
    :rtype: Any
    """

    query = """
    INSERT INTO v1.students_course_sections (students_id, course_sections_id, is_completed)
    VALUES ($1, $2, TRUE)
    ON CONFLICT (students_id, course_sections_id)
    DO UPDATE SET is_completed = TRUE
    """
    return await insert_data_func(query, (student_id, section_id))

async def get_completed_sections_repo(student_id: int, course_id: int, get_data_func=read_query):
    """
    Retrieve the IDs of completed course sections for a student in a given course.

    This function interacts with a database to fetch the IDs of course sections
    that a specific student has completed. The course sections are determined
    based on the provided course ID and student ID. The function is asynchronous
    and uses a callback function to execute the database query.

    :param student_id: The unique identifier of the student.
    :type student_id: int
    :param course_id: The unique identifier of the course.
    :type course_id: int
    :param get_data_func: A callable function used to execute the database query.
        Defaults to `read_query`.
    :return: A list of IDs of the completed course sections for the specified student
        and course.
    :rtype: List[int]
    """
    query = """
    SELECT cs.id
    FROM v1.students_course_sections scs
    JOIN v1.course_sections cs ON cs.id = scs.course_sections_id
    WHERE scs.students_id = $1
        AND cs.course_id = $2
        AND scs.is_completed = TRUE
    """
    return await get_data_func(query, (student_id, course_id))