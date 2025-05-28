import psycopg2
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from psycopg2.extensions import connection as Connection

load_dotenv(dotenv_path="external_keys.env")

DATABASE_URL = os.getenv("DATABASE_URL")
KEY = os.getenv("KEY")

# supabase: Client = create_client(DATABASE_URL, KEY)

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DATABASE = os.getenv("dbname")

# Connect to the database
def Connection_supabase() -> Connection:
    return psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DATABASE
    )