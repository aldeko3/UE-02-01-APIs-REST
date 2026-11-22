import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
    )
    cursor = connection.cursor()

    schema_path = Path(__file__).parent / "schema.sql"
    sql_script = schema_path.read_text(encoding="utf-8")

    for statement in sql_script.split(";"):
        stmt = statement.strip()
        if stmt:
            cursor.execute(stmt)

    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    run_migrations()
    print("Base de datos y tablas inicializadas correctamente.")