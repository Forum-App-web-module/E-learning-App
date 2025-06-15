from repositories.student_repo import is_subscribed_repo, subscribe_repo
from asyncpg import UniqueViolationError
from fastapi import HTTPException
from data.models import Subscription, SubscriptionResponse

async def is_subscribed(student_id):
    record = await is_subscribed_repo(student_id)
    if record:
        return SubscriptionResponse(
            id=record['id'],
            student_id=record['student_id'],
            subscribed_at=record['subscribed_at'],
            expire_date=record['expire_date']
        ).model_dump()
    else:
        return None
        
    
async def subscribe(student_id):
    try: 
        subscription = Subscription(student_id=student_id)
        await subscribe_repo(student_id, subscription)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="Student is already subscribed for premium account!")
    return await is_subscribed(student_id)


    
