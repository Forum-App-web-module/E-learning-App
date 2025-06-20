from data.models import SectionCreate, SectionUpdate, UserRole
from data.database import insert_query, update_query, read_query

async def insert_section_repo(course_id: int, section: SectionCreate, insert_data_func = insert_query):
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

    query = """
    INSERT INTO v1.students_course_sections (students_id, course_sections_id, is_completed)
    VALUES ($1, $2, TRUE)
    ON CONFLICT (students_id, course_sections_id)
    DO UPDATE SET is_completed = TRUE
    """
    return await insert_data_func(query, (student_id, section_id))

async def get_completed_sections_repo(student_id: int, course_id: int, get_data_func=read_query):
    query = """
    SELECT cs.id
    FROM v1.students_course_sections scs
    JOIN v1.course_sections cs ON cs.id = scs.course_sections_id
    WHERE scs.students_id = $1
        AND cs.course_id = $2
        AND scs.is_completed = TRUE
    """
    return await get_data_func(query, (student_id, course_id))