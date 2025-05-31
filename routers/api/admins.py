from fastapi import APIRouter




admins_router = APIRouter(prefix="/admins", tags=["admins"])

# approve teacher registration - get from email link
@admins_router.get("/email/{id}")
async def approve_email():
    pass
