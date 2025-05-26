from fastapi import FastAPI
import uvicorn
from routers.api.auth import auth_router
from routers.users import users_router
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.include_router(auth_router)
app.include_router(users_router)








if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)