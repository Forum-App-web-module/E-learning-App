# from data.database import query_count
# from hashlib import sha256
# from dotenv import load_dotenv
# from os import getenv

# load_dotenv(dotenv_path="key_example.env")

# SALT = getenv("SALT")

# def hash_password(password: str):
#     solted = password + SALT
#     return sha256(solted.encode("utf-8")).hexdigest()






from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) ->str:
    return password_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)