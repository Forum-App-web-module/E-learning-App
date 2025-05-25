from data.database import query_count
from hashlib import sha256
from dotenv import load_dotenv
from os import getenv

load_dotenv(dotenv_path="key_example.env")

SALT = getenv("SALT")

def hash_password(password: str):
    solted = password + SALT
    return sha256(solted.encode("utf-8")).hexdigest()