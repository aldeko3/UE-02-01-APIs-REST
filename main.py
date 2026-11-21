import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from models.models import UserCreate, UserUpdate
from configuration.connections import get_db_connection
from services.twitch_service import get_streamer_data

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ue_02_01_apis_rest_twitch")

app = FastAPI()

def get_db():
    return get_db_connection(
        host = MYSQL_HOST,
        user = MYSQL_USER,
        password = MYSQL_PASSWORD,
        database = MYSQL_DATABASE
    )

@app.get("/")
def root():
    return {"message": "Hola Mundo!"}

@app.get("/users")
async def get_users():
    connection = get_db()
    myCursor = connection.cursor(dictionary=True) #diferencia (DOC)

    myCursor.execute('SELECT * FROM users;')
    res = myCursor.fetchall()

    myCursor.close()#diferencia (DOC)
    connection.close()#diferencia (DOC)
    return res

@app.post("/users")
async def create_user(user: UserCreate):
    connection = get_db()
    myCursor = connection.cursor()

    query = """
        INSERT INTO `users` (username, first_name, first_surname, second_surname, email)
        VALUES (%s, %s, %s, %s, %s);
    """
    values = (
        user.username,
        user.first_name,
        user.first_surname,
        user.second_surname,
        user.email,
    )
    myCursor.execute(query, values)
    connection.commit()

    myCursor.close()
    connection.close()

    return JSONResponse(
        content={"message": "User added successfully"},
        status_code=201,
    )

@app.put("/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    connection = get_db()
    myCursor = connection.cursor()

    update_fields=[]
    if user.username is not None:
        update_fields.append(f'username="{user.username}"')
    if user.first_name is not None:
        update_fields.append(f'first_name="{user.first_name}"')
    if user.first_surname is not None:
        update_fields.append(f'first_surname="{user.first_surname}"')
    if user.second_surname is not None:
        update_fields.append(f'second_surname="{user.second_surname}"')
    if user.email is not None:
        update_fields.append(f'email="{user.email}"')
    if not update_fields:
        myCursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    myCursor.execute(f'UPDATE `users` SET {", ".join(update_fields)} WHERE id={user_id};')
    connection.commit()
    
    myCursor.close()
    connection.close()

    if myCursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return JSONResponse(
        content={"message": "User updated successfully"},
        status_code=200,
    )

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    connection = get_db()
    myCursor = connection.cursor()
    myCursor.execute("DELETE FROM `users` WHERE id = %s;", (user_id,))
    connection.commit()
    myCursor.close()
    connection.close()

    if myCursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return JSONResponse(
        content={"message": "User deleted successfully"},
        status_code=200,
    )

@app.get("/twitch/streamers/{login}")
async def get_twitch_streamer(login: str):
    data = get_streamer_data(login, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return JSONResponse(content=data, status_code=200)

@app.get("/users/{user_id}/favourites")
async def get_user_favorite_streamers(user_id: int):
    connection = get_db()
    myCursor = connection.cursor()

    myCursor.execute("SELECT id FROM `users` WHERE id = %s;", (user_id,)) #user_id, con la coma
    if not myCursor.fetchone(): #if myCursor.rowcount == 0: eso no vale
        myCursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    myCursor.execute("SELECT * FROM `favorite_streamers` WHERE user_id = %s;", (user_id,))
    favorites = myCursor.fetchall()

    myCursor.close()
    connection.close()

    return favorites


# app.post("/users/{user_id}/favorites")
# def add_favorite_streamer(user_id: int, favorite: FavoriteStreamerCreate):
#     streamer_data = get_streamer_data(favorite.login, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
#     if "error" in streamer_data:
#         raise HTTPException(status_code=404, detail=streamer_data["error"])

#     connection = get_db()
#     myCursor = connection.cursor()

#     myCursor.execute("SELECT id FROM `users` WHERE id = %s;", (user_id,))
#     if not myCursor.fetchone():
#         myCursor.close()
#         connection.close()
#         raise HTTPException(status_code=404, detail="User not found")

#     query = """
#         INSERT INTO `favorite_streamers` (user_id, twitch_streamer_id, twitch_streamer_login)
#         VALUES (%s, %s, %s);
#     """
#     values = (
#         user_id,
#         streamer_data["twitch_streamer_id"],
#         streamer_data["login"],
#     )
#     try:
#         myCursor.execute(query, values)
#         connection.commit()
#     except Error:
#         connection.rollback()
#         raise HTTPException(status_code=400, detail="Streamer is already in user's favorites")
#     finally:
#         myCursor.close()
#         connection.close()

#     return JSONResponse(
#         content={"message": f"Streamer '{streamer_data['login']}' added to favorites"},
#         status_code=201,
#     )


# @app.delete("/users/{user_id}/favorites/{twitch_streamer_id}")
# def delete_favorite_streamer(user_id: int, twitch_streamer_id: str):
#     connection = get_db()
#     myCursor = connection.cursor()
#     myCursor.execute(
#         "DELETE FROM `favorite_streamers` WHERE user_id = %s AND twitch_streamer_id = %s;",
#         (user_id, twitch_streamer_id),
#     )
#     connection.commit()
#     affected = myCursor.rowcount

#     myCursor.close()
#     connection.close()

#     if affected == 0:
#         raise HTTPException(status_code=404, detail="Favorite streamer not found for this user")

#     return JSONResponse(
#         content={"message": "Favorite streamer removed successfully"},
#         status_code=200,
#     )