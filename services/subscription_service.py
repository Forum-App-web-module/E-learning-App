from data.models import Subscription
from data import database
from repositories.student_repo import repo_is_subscribed, repo_subscribe
from asyncpg import UniqueViolationError
from fastapi import HTTPException

async def is_subscribed(student_id):
    await repo_is_subscribed(student_id)

async def subscribe(student_id):
    try: 
        await repo_subscribe(student_id)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="Student is already subscribed for premium account!")


    
