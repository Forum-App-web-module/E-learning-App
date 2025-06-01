
from data.database import update_query, insert_query, read_query





async def repo_update_avatar_url(url: str, user_email, update_data_func = update_query): 
    query = "UPDATE v1.students SET avatar_url = $1 WHERE email = $2"
    id = await update_data_func(query, (url, user_email))
    return id


async def repo_subscribe(student_id, insert_data_func = insert_query):
    query = "INSERT INTO v1.subscriptions (student_id) VALUES ($1) RETURNING id"
    id = await insert_data_func(query, (student_id,))
    return id


async def repo_is_subscribed(student_id, get_data_func = read_query):
    query = "SELECT student_id, subscribed_at, expire_date FROM subscriptions WHERE student_id = $1"
    subscription = await get_data_func(query, (student_id,))
    return subscription if subscription else None