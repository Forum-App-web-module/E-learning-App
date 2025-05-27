from fastapi import APIRouter
from fastapi.params import Depends
from controllers import teacher_controller

users_router = APIRouter(prefix="/teachers", tags=["teachers"])


@users_router.get("/")
async def get_teachers(token: Depends()):
    return teacher_controller.get_account_by_email(token)



