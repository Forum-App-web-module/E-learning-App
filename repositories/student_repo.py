
from data.database import update_query





async def repo_update_avatar_url(url: str, user_email, update_data_func = update_query): 
    query = "UPDATE v1.students SET avatar_url = $1 WHERE email = $2"
    id = await update_query(query, (url, user_email))
    return id