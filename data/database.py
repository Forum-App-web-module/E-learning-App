import asyncpg
from typing import Any, Sequence, Union
from config.database_deploy_config import connection_supabase
from os import getenv
from dotenv import load_dotenv


# load_dotenv(dotenv_path="external_keys.env")
# USE_DEPLOYED_DB = getenv("USE_DEPLOYED_DB", "true").lower() == "true"


async def _get_connection()-> asyncpg.Connection:
    return await asyncpg.connect(**connection_supabase())

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

