from fastapi import FastAPI
import uvicorn
from routers.api.auth import auth_router
from routers.api.students import students_router
from routers.api.teachers import teachers_router
from routers.api.courses import courses_router
from routers.api.admins import admins_router
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.include_router(auth_router)
app.include_router(students_router)
app.include_router(courses_router)
app.include_router(admins_router)
app.include_router(teachers_router)




if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)