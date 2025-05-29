from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from data.models import LoginData, StudentRegisterData, TeacherRegisterData, UserRole
from services.user_service import email_exists, create_account, get_hash_by_email
from common import responses
from typing import Union
from security import secrets
from security.jwt_auth import create_access_token
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from dotenv import load_dotenv
import os

auth_router = APIRouter(prefix="", tags=["Auth"])

load_dotenv()
config = Config(environ=os.environ)
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'email profile'}
)

@auth_router.post('/login')
def login(login: LoginData):
    if not email_exists(login.email):
        return responses.Unauthorized("Wrong Credentials!")
    
    hashed_pw = get_hash_by_email(login.email)
    if not secrets.verify_password(login.password, hashed_pw):
        return responses.Unauthorized("Wrong Credentials!")
    
    username = email_exists(login.email)
    token = create_access_token({"sub": username['email'], "role": username['role']})
    
    return {"access_token": token["JWT"], "token_type": "bearer"}

@auth_router.post('/register')
async def register(register_data: Union[TeacherRegisterData, StudentRegisterData]):
    if await email_exists(register_data.email):
        return responses.BadRequest(content="Email already registered.")
    
    role, role_id = await create_account(register_data, secrets.hash_password(register_data.password))

    return responses.Created(content={
        "message": f"New User is registered.",
        "role": role.value,
        "id": role_id
    })

# login redirect to google
"""
Redirect to google for Oauth2
Redirect uri is generated: auth_google_callback, should be the same as in Google cloud console

"""
@auth_router.get("/login/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    print("Redirect uri:", redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)

"""
Callback to Google after successful login
Get token and user data from google
Create an account if it does not exist
Return JWT token 
"""
@auth_router.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    google_responce = await oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
    user_data = google_responce.json()

    email = user_data["email"]
    name = user_data.get("name", "")

    user = email_exists(email)
    if not user:
        student = StudentRegisterData(
            email=email,
            password="GOOGLE_AUTH"
        )
        create_account(student, hashed_password="GOOGLE_AUTH")

#returning html for testing purposes
    jwt_token = create_access_token({"sub": email, "auth_source": "google"})
    return HTMLResponse(f"""
        <h2>Добре дошъл, {name}!</h2>
    """)


    