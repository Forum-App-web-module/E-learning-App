from data.models import Section, SectionCreate, CourseUpdate, SectionUpdate
from data.database import insert_query, update_query, read_query

async def insert_section(course_id: int, section: SectionCreate, insert_data_func = insert_query):
    query = """
        INSERT INTO v1.course_sections (title, course_id, content, description)
        VALUES ($1, $2, $3, $4)
        RETURNING id
"""

    data = (
        section.title,
        course_id,
        section.content,
        section.description
    )

    result  = await insert_data_func(query, data)
    return result if result else None

async def update_section(id: int, updates: SectionUpdate, update_data_func = update_query):
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

async def get_all_course_sections_repo(id: int, sort_by: str = "id", order: str = "asc", get_data_func = read_query):
    
    sorting_options = {"id", "title"}
    order_options = {"asc","desc"}

    if sort_by not in sorting_options:
        sort_by = "id"

    if order not in order_options:
        order = "asc"

    query = f"""
    SELECT * FROM v1.course_sections
    WHERE course_id = $1
    ORDER BY {sort_by} {order}
"""

    all_sections = await get_data_func(query, (id, ))
    return all_sections if all_sections else None