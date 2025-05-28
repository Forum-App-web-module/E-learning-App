import asyncpg
from typing import Any, Sequence, Union
import psycopg2
from psycopg2.extensions import connection as Connection
from data.database_deploy_config import Connection_supabase
from os import getenv
from dotenv import load_dotenv


load_dotenv(dotenv_path="external_keys.env")
USE_DEPLOYED_DB = getenv("USE_DEPLOYED_DB", "true").lower() == "true"

import asyncpg
from typing import Any, Sequence, Union

async def _get_connection() -> Connection:
    if USE_DEPLOYED_DB:
        return await Connection_supabase()
    else:
        return await psycopg2.connect(
            user='postgres',
            password='1997',
            host='localhost',
            port=5432,
            dbname='E-learning'
        )

async def read_query(sql: str, sql_params: Union[Sequence[Any], dict] = ()):
    conn = await _get_connection()
    try:
        # When parameters are not list, tuple, pass a dictionary
        return await conn.fetch(sql, *sql_params) if isinstance(sql_params, (list, tuple)) else await conn.fetch(sql, **sql_params)
    finally:
        await conn.close()

async def insert_query(sql: str, sql_params: Union[Sequence[Any], dict] = ()):
    conn = await _get_connection()
    try:
        result = await conn.fetchrow(sql, *sql_params) if isinstance(sql_params, (list, tuple)) else await conn.fetchrow(sql, **sql_params)
        return result[0] if result else None
    finally:
        await conn.close()

async def update_query(sql: str, sql_params: Union[Sequence[Any], dict] = ()) -> int:
    conn = await _get_connection()
    try:
        result = await conn.execute(sql, *sql_params) if isinstance(sql_params, (list, tuple)) else await conn.execute(sql, **sql_params)
        # The result is a string like "UPDATE 1" — extract the row count
        return int(result.split()[-1])
    finally:
        await conn.close()

async def query_count(sql: str, sql_params: Union[Sequence[Any], dict] = ()) -> int:
    conn = await _get_connection()
    try:
        result = await conn.fetchrow(sql, *sql_params) if isinstance(sql_params, (list, tuple)) else await conn.fetchrow(sql, **sql_params)
        return result[0] if result else 0
    finally:
        await conn.close()




