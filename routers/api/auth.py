from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from data.models import LoginData, StudentRegisterData, TeacherRegisterData, UserRole
from services.user_service import email_exists, create_account, get_hash_by_email, get_role_by_email
from common import responses
from typing import Union
from security import secrets
from security.jwt_auth import create_access_token
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from dotenv import load_dotenv
from repositories.user_repo import get_account_by_email_repo
import os
from security.secrets import verify_password
from services.teacher_service import get_teacher_by_id
from config.mailJet_config import teacher_verify_email, admin_teacher_aproval


auth_router = APIRouter(prefix="", tags=["Auth"])

load_dotenv()
admin_email=os.getenv("ADMIN_EMAIL")

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

async def _authenticate_user(email: str, password: str):

    if not await email_exists(email):
        return responses.Unauthorized("Wrong Credentials!")
    
    hashed_pw = await get_hash_by_email(email)
    if not verify_password(password, hashed_pw):
        return responses.Unauthorized("Wrong Credentials!")

    role = await get_role_by_email(email)

    profile = await get_account_by_email_repo(email, role)
    if profile.get("is_active") == False:
        if role == UserRole.STUDENT:
            return responses.Unauthorized(content=f"This accound is blocked by admin. Please contact ADMIN team at {admin_email}.")
        elif role == UserRole.TEACHER:
            return responses.Unauthorized(content=f"Your account is being processed still. Expect notification when accound is acticated. In case of trouble contact us at {admin_email}.")

    profile = dict(profile)
    profile["role"] = role
    token = create_access_token(dict(profile))
    
    return responses.Successful(content={"access_token": token["JWT"], "token_type": "bearer"})


@auth_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return an access token.

This endpoint uses OAuth2PasswordRequestForm for login with email and password.
The access token returned can be used to authorize protected endpoints.

Parameters:
    form_data (OAuth2PasswordRequestForm): Form containing `username` (email) and `password`.

Returns:
    JSON with access token and token type, or an error message if credentials are invalid.
"""
    email = form_data.username
    password = form_data.password

    return await _authenticate_user(email, password)

@auth_router.post('/login')
async def login(login: LoginData):
    """
    Log in a user using email and password (JSON payload).

This is a standard login endpoint accepting credentials in the request body.
Returns a JWT access token if credentials are valid.

Parameters:
    login (LoginData): User login credentials.

Returns:
    JWT access token and token type, or an error message if authentication fails
"""
    return await _authenticate_user(login.email, login.password)


@auth_router.post('/register')
async def register(register_data: Union[TeacherRegisterData, StudentRegisterData]):
    """
    Register a new student or teacher account.

Based on the data provided, the user is registered as either a student or teacher.
- Teachers receive a verification email and await admin approval.
- Students are immediately active unless blocked.

Parameters:
    register_data (TeacherRegisterData | StudentRegisterData): Registration information.

Returns:
    A message confirming registration, the user role, and new user ID.
"""
    if await email_exists(register_data.email):
        return responses.BadRequest(content="Email already registered.")
    
    role, role_id = await create_account(register_data, secrets.hash_password(register_data.password))

    if role == UserRole.TEACHER:
        teacher_object = await get_teacher_by_id(role_id)
        await teacher_verify_email(teacher_object, role_id)
        await admin_teacher_aproval(teacher_object)
        
    return responses.Created(content={
        "message": f"New User is registered.",
        "role": role.value,
        "id": role_id
    })

# login redirect to google
@auth_router.get("/login/google")
async def google_login(request: Request):
    """
    Initiate Google OAuth2 login flow.
Redirects the user to Google's authentication page. After successful login,
Google redirects back to your app via the configured callback.

Parameters:
    request (Request): Incoming HTTP request.

Returns:
    Redirect response to Google's OAuth2 login page.
"""
    redirect_uri = request.url_for("auth_google_callback")
    print("Redirect uri:", redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_router.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    """
    Handle Google OAuth2 callback and log in the user.

After a successful Google login, this endpoint:
- Retrieves user info from Google.
- Creates a student account if not already registered.
- Issues a JWT token to authenticate further requests.

Parameters:
    request (Request): The request object from Google's redirect.
    
Returns:
    JSON response with a JWT token.
"""
    token = await oauth.google.authorize_access_token(request)
    google_responce = await oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
    user_data = google_responce.json()

    email = user_data["sub"]
    name = user_data.get("name", "")

    user = email_exists(email)
    if not user:
        student = StudentRegisterData(
            email=email,
            password="GOOGLE_AUTH"
        )
        create_account(student, hashed_password="GOOGLE_AUTH")

    _authenticate_user(email=email, password="GOOGLE_AUTH")

    jwt_token = create_access_token({"sub": email, "auth_source":"google"})
    return JSONResponse({"access_token": jwt_token, "token_type": "bearer"})




