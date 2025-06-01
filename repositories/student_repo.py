
from data.database import update_query, insert_query, read_query
from data.models import Subscription




async def repo_update_avatar_url(url: str, user_email, update_data_func = update_query): 
    query = "UPDATE v1.students SET avatar_url = $1 WHERE email = $2"
    id = await update_data_func(query, (url, user_email))
    return id


async def repo_subscribe(student_id, subscription: Subscription, insert_data_func = insert_query):
    query = "INSERT INTO v1.subscriptions (student_id, expire_date) VALUES ($1, $2) RETURNING id"
    id = await insert_data_func(query, (student_id, subscription.expire_date))
    return id


async def repo_is_subscribed(student_id, get_data_func = read_query):
    query = "SELECT id, student_id, subscribed_at, expire_date FROM v1.subscriptions WHERE student_id = $1"
    subscription = await get_data_func(query, (student_id,))
    return subscription[0] if subscription else None