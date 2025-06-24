"""
Database helper functions for executing SQL queries using asyncpg.
Each function opens a connection, runs the query, and closes the connection.
"""


import asyncpg
from typing import Any, Sequence, Union
from config.database_deploy_config import connection_supabase
from os import getenv
from dotenv import load_dotenv


async def _get_connection()-> asyncpg.Connection:
    """Open a new asyncpg connection using Supabase or Local configuration."""
    return await asyncpg.connect(**connection_supabase())

async def read_query(sql: str, sql_params: Union[Sequence[Any], dict] = ()):
    """Execute a SELECT query and return all rows."""
    conn = await _get_connection()
    try:
        # When parameters are not list, tuple, pass a dictionary
        return await conn.fetch(sql, *sql_params) if isinstance(sql_params, (list, tuple)) else await conn.fetch(sql, **sql_params)
    finally:
        await conn.close()

async def insert_query(sql: str, sql_params: Union[Sequence[Any], dict] = ()):
    """Execute an INSERT query and return the first column of the first row (e.g., inserted ID)."""
    conn = await _get_connection()
    try:
        result = await conn.fetchrow(sql, *sql_params) if isinstance(sql_params, (list, tuple)) else await conn.fetchrow(sql, **sql_params)
        return result[0] if result else None
    finally:
        await conn.close()

async def update_query(sql: str, sql_params: Union[Sequence[Any], dict] = ()) -> int:
    """Execute an UPDATE query and return the number of affected rows."""
    conn = await _get_connection()
    try:
        result = await conn.execute(sql, *sql_params) if isinstance(sql_params, (list, tuple)) else await conn.execute(sql, **sql_params)
        # The result is a string like "UPDATE 1" — extract the row count
        return int(result.split()[-1])
    finally:
        await conn.close()

async def query_count(sql: str, sql_params: Union[Sequence[Any], dict] = ()) -> int:
    """Execute a COUNT query and return the count as an integer."""
    conn = await _get_connection()
    try:
        result = await conn.fetchrow(sql, *sql_params) if isinstance(sql_params, (list, tuple)) else await conn.fetchrow(sql, **sql_params)
        return result[0] if result else 0
    finally:
        await conn.close()

