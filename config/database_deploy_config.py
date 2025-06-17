from typing import Any
from os import getenv
from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv(dotenv_path=".env")

DATABASE_URL = getenv("DATABASE_URL")
KEY = getenv("KEY")

# supabase: Client = create_client(DATABASE_URL, KEY)


DB_CONFIG_LOCAL = {
    "user": "postgres",
    "password": "1997",
    "host": "localhost",
    "port": 5432,
    "database": "E-learning"
}

DB_CONFIG_HOSTED = {
    "user": getenv("USER"),
    "password": getenv("PASSWORD"),
    "host": getenv("HOST"),
    "port": getenv("PORT"),
    "database": getenv("DBNAME")
}

# Connect details
def connection_supabase() -> dict:
    return DB_CONFIG_HOSTED if getenv("USE_DEPLOYED_DB", "true").lower() == "true" else DB_CONFIG_LOCAL

