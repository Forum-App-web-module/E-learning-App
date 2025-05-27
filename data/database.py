import asyncpg
from typing import Any, Sequence, Union

DB_CONFIG = {
    "user": "postgres",
    "password": "1997",
    "host": "localhost",
    "port": 5432,
    "database": "E-learning"
}

async def _get_connection():
    return await asyncpg.connect(**DB_CONFIG)

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


# import psycopg2
# from psycopg2.extensions import connection as Connection
#
#
# def _get_connection() -> Connection:
#     return psycopg2.connect(
#         user='postgres',
#         password='1997',
#         host='localhost',
#         port=5432,
#         dbname='E-learning'
#     )
#
#
# def read_query(sql: str, sql_params=()):
#     with _get_connection() as conn:
#         with conn.cursor() as cursor:
#             cursor.execute(sql, sql_params)
#             return cursor.fetchall()
#
#
# def insert_query(sql: str, sql_params=()):
#     with _get_connection() as conn:
#         with conn.cursor() as cursor:
#             cursor.execute(sql, sql_params)
#             conn.commit()
#             try:
#                 return cursor.fetchone()[0]
#             except (TypeError, IndexError):
#                 return cursor.rowcount
#
#
# def update_query(sql: str, sql_params=()) -> int:
#     with _get_connection() as conn:
#         with conn.cursor() as cursor:
#             cursor.execute(sql, sql_params)
#             conn.commit()
#             return cursor.rowcount
#
#
# def query_count(sql: str, sql_params=()) -> int:
#     with _get_connection as conn:
#         with conn.cursor as cursor:
#             cursor.execute(sql, sql_params)
#             return cursor.rowcount


