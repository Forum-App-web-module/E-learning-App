from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request
from dotenv import load_dotenv
from os import getenv


SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"JWT": token}


