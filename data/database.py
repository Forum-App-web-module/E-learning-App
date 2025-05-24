import psycopg2
from psycopg2.extensions import connection as Connection

def _get_connection() -> Connection:
    return psycopg2.connect(
        user='postgres',
        password='1997',
        host='localhost',
        port=5432,
        dbname='E-learning'
    )

def read_query(sql: str, sql_params=()):
    with _get_connection as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, sql_params)
            return cursor.fetchall()
        
def insert_query(sql: str, sql_params=()):
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, sql_params)
            conn.commit()
            try:
                return cursor.fetchone()[0]
            except (TypeError, IndexError):
                return cursor.rowcount
                
def update_query(sql: str, sql_params=()) -> int:
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, sql_params)
            conn.commit()
            return cursor.rowcount
        

def query_count(sql: str, sql_params=()) -> int:
    with _get_connection as conn:
        with conn.cursor as cursor:
            cursor.execute(sql, sql_params)
            return cursor.rowcount

