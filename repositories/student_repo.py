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
            SET first_name = $1,
                last_name = $2,
                avatar_url = $3
            WHERE email = $4
            """
    student = await update_data_func(query, (first_name, last_name, avatar_url, user_email))
    return student

async def repo_update_avatar_url(url: str, user_email, update_data_func = update_query): 
    query = "UPDATE v1.students SET avatar_url = $1 WHERE email = $2"
    student_id = await update_data_func(query, (url, user_email))
    return student_id


async def repo_subscribe(student_id, subscription: Subscription, insert_data_func = insert_query):
    query = "INSERT INTO v1.subscriptions (student_id, expire_date) VALUES ($1, $2) RETURNING id"
    new_id = await insert_data_func(query, (student_id, subscription.expire_date))
    return new_id


async def repo_is_subscribed(student_id, get_data_func = read_query):
    query = "SELECT id, student_id, subscribed_at, expire_date FROM v1.subscriptions WHERE student_id = $1"
    subscription = await get_data_func(query, (student_id,))
    return subscription[0] if subscription else None