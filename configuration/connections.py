import mysql.connector
from fastapi import HTTPException
from mysql.connector import Error

def get_db_connection(host: str, user: str, password: str, database: str):
    try:
        return mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a MySQL: {e!s}")