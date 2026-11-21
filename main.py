import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from mysql.connector import Error

from models.models import (
    UserCreate,
    UserUpdate,
    FavoriteStreamerCreate,
    PlaylistCreate,
    PlaylistItemCreate,
)
from configuration.connections import get_db_connection
from services.twitch_service import (
    get_streamer_data,
    get_streamer_videos,
    get_video_by_id,
)
# from database.init_db import run_migrations

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ue_02_01_apis_rest_twitch")

# Con información para la documentación
app = FastAPI(
    title = "Twitch Streamers & Playlists API",
    description = "API REST desarrollada con FastAPI y MySQL integrada con la API oficial de Twitch.",
    version = "1.0.0",
    openapi_tags = [
        {"name": "General", "description": "Comprobación de estado de la API."},
        {"name": "Usuarios", "description": "Gestión de usuarios almacenados en MySQL."},
        {"name": "Twitch", "description": "Consultas en tiempo real a la API de Twitch."},
        {"name": "Favoritos", "description": "Streamers favoritos asociados a cada usuario."},
        {"name": "Playlists", "description": "Colecciones personalizadas de vídeos de Twitch."},
    ]
)

def get_db():
    return get_db_connection(
        host = MYSQL_HOST,
        user = MYSQL_USER,
        password = MYSQL_PASSWORD,
        database = MYSQL_DATABASE,
    )


# --------------------------- #
# --------- GENERAL --------- #
# --------------------------- #


#He cambiado de "/" a "/health" porque veía en consola que se quejaba "GET /health HTTP/1.1" 404 Not Found
@app.get("/health", tags = ["General"], summary = "Comprobación de estado de la API.")
def root():
    return {"message": "Hola Mundo!"}


# --------------------------- #
# ---------- USUARIOS ------- #
# --------------------------- #


#he visto que por una regla de REST mejor en plural
@app.get("/users", tags = ["Usuarios"], summary = "Listar todos los usuarios")
def get_users():
    connection = get_db()
    myCursor = connection.cursor(dictionary = True)

    myCursor.execute("SELECT * FROM users;")
    res = myCursor.fetchall()

    # importante cerrar el cursor y la conexión
    myCursor.close() 
    connection.close()
    return res


@app.post("/users", tags = ["Usuarios"], summary = "Crear un nuevo usuario")
def create_user(user: UserCreate):
    connection = get_db()
    myCursor = connection.cursor()

    #Cuando la ejecución de la quiery es muy larga se pueden sacar a variables la query y los valores
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
        content = {"message": "User added successfully"},
        status_code = 201,
    )


@app.put("/users/{user_id}", tags = ["Usuarios"], summary = "Actualizar un usuario existente")
def update_user(user_id: int, user: UserUpdate):
    connection = get_db()
    myCursor = connection.cursor()

    update_fields = []
    if user.username is not None:
        update_fields.append(f'username = "{user.username}"')
    if user.first_name is not None:
        update_fields.append(f'first_name = "{user.first_name}"')
    if user.first_surname is not None:
        update_fields.append(f'first_surname = "{user.first_surname}"')
    if user.second_surname is not None:
        update_fields.append(f'second_surname = "{user.second_surname}"')
    if user.email is not None:
        update_fields.append(f'email = "{user.email}"')

    if not update_fields:
        myCursor.close()
        connection.close()
        raise HTTPException(status_code = 400, detail = "No hay campos para actualizar")

    myCursor.execute(f'UPDATE `users` SET {", ".join(update_fields)} WHERE id = {user_id};')
    connection.commit()
    affected = myCursor.rowcount

    myCursor.close()
    connection.close()

    if affected == 0:
        raise HTTPException(status_code = 404, detail = "Usuario no encontrado")

    return JSONResponse(
        content = {"message": "User updated successfully"},
        status_code = 200,
    )


@app.delete("/users/{user_id}", tags = ["Usuarios"], summary = "Eliminar un usuario")
def delete_user(user_id: int):
    connection = get_db()
    myCursor = connection.cursor()

    myCursor.execute("DELETE FROM `users` WHERE id = %s;", (user_id,)) #user_id, con la coma
    connection.commit()
    affected = myCursor.rowcount

    myCursor.close()
    connection.close()

    if affected == 0:
        raise HTTPException(status_code = 404, detail = "Usuario no encontrado")

    return JSONResponse(
        content = {"message": "User deleted successfully"},
        status_code = 200,
    )


# --------------------------- #
# --------- TWITCH ---------- #
# --------------------------- #

@app.get("/twitch/streamers/{login}", tags = ["Twitch"], summary = "Buscar datos de un streamer en Twitch")
def get_twitch_streamer(login: str):
    streamer_data = get_streamer_data(login, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
    if "error" in streamer_data:
        raise HTTPException(status_code = 404, detail = streamer_data["error"])
    return JSONResponse(content = streamer_data, status_code = 200)


@app.get("/twitch/streamers/{login}/videos", tags = ["Twitch"], summary = "Listar últimos vídeos/VODs de un streamer")
def get_twitch_streamer_videos(login: str):
    data = get_streamer_videos(login, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
    if "error" in data:
        raise HTTPException(status_code = 404, detail = data["error"])
    return JSONResponse(content = data, status_code = 200)


# --------------------------- #
# --- STREAMERS FAVORITOS --- #
# --------------------------- #

@app.get("/users/{user_id}/favorites", tags = ["Favoritos"], summary = "Listar streamers favoritos de un usuario")
def get_user_favorite_streamers(user_id: int):
    connection = get_db()
    myCursor = connection.cursor(dictionary = True)

    myCursor.execute("SELECT id FROM `users` WHERE id = %s;", (user_id,))
    if not myCursor.fetchone(): #if myCursor.rowcount == 0: eso no vale
        myCursor.close()
        connection.close()
        raise HTTPException(status_code = 404, detail = "Usuario no encontrado")

    myCursor.execute("SELECT * FROM `favorite_streamers` WHERE user_id = %s;", (user_id,))
    favorites = myCursor.fetchall()

    myCursor.close()
    connection.close()

    return favorites


@app.post("/users/{user_id}/favorites", tags = ["Favoritos"], summary = "Añadir un streamer a favoritos")
def add_favorite_streamer(user_id: int, favorite: FavoriteStreamerCreate):
    streamer_data = get_streamer_data(favorite.login, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
    if "error" in streamer_data:
        raise HTTPException(status_code = 404, detail = streamer_data["error"])

    connection = get_db()
    myCursor = connection.cursor()

    myCursor.execute("SELECT id FROM `users` WHERE id = %s;", (user_id,))
    if not myCursor.fetchone():
        myCursor.close()
        connection.close()
        raise HTTPException(status_code = 404, detail = "Usuario no encontrado")

    query = """
        INSERT INTO `favorite_streamers` (user_id, twitch_streamer_id, twitch_streamer_login)
        VALUES (%s, %s, %s);
    """
    values = (
        user_id,
        streamer_data["twitch_streamer_id"],
        streamer_data["login"],
    )
    try:
        myCursor.execute(query, values)
        connection.commit()
    except Error:
        connection.rollback()
        raise HTTPException(status_code = 400, detail = "El streamer ya está en los favoritos del usuario")
    finally:
        myCursor.close()
        connection.close()

    return JSONResponse(
        content = {"message": f"Streamer '{streamer_data['login']}' added to favorites"},
        status_code = 201,
    )


@app.delete("/users/{user_id}/favorites/{twitch_streamer_id}", tags = ["Favoritos"], summary = "Eliminar un streamer de favoritos",)
def delete_favorite_streamer(user_id: int, twitch_streamer_id: str):
    connection = get_db()
    myCursor = connection.cursor()

    myCursor.execute("SELECT id FROM `users` WHERE id = %s;", (user_id,))
    if not myCursor.fetchone():
        myCursor.close()
        connection.close()
        raise HTTPException(status_code = 404, detail = "Usuario no encontrado")

    myCursor.execute(
        "DELETE FROM `favorite_streamers` WHERE user_id = %s AND twitch_streamer_id = %s;",
        (user_id, twitch_streamer_id),
    )
    connection.commit()
    affected = myCursor.rowcount

    myCursor.close()
    connection.close()

    if affected == 0:
        raise HTTPException(status_code = 404, detail = "Streamer favorito no encontrado para este usuario")

    return JSONResponse(
        content = {"message": "Favorite streamer removed successfully"},
        status_code = 200,
    )


# --------------------------- #
# -------- PLAYLISTS -------- #
# --------------------------- #

@app.get("/users/{user_id}/playlists", tags = ["Playlists"], summary = "Listar playlists y vídeos de un usuario")
def get_user_playlists(user_id: int):
    connection = get_db()
    myCursor = connection.cursor(dictionary = True)

    myCursor.execute("SELECT id FROM `users` WHERE id = %s;", (user_id,))
    if not myCursor.fetchone():
        myCursor.close()
        connection.close()
        raise HTTPException(status_code = 404, detail = "Usuario no encontrado")

    myCursor.execute("SELECT * FROM `playlists` WHERE user_id = %s;", (user_id,))
    playlists = myCursor.fetchall()

    for playlist in playlists:
        myCursor.execute(
            "SELECT * FROM `playlist_items` WHERE playlist_id = %s;",
            (playlist["id"],),
        )
        playlist["videos"] = myCursor.fetchall()

    myCursor.close()
    connection.close()

    return playlists


@app.post("/users/{user_id}/playlists", tags = ["Playlists"], summary = "Crear una nueva playlist")
def create_playlist(user_id: int, playlist: PlaylistCreate):
    connection = get_db()
    myCursor = connection.cursor()

    myCursor.execute("SELECT id FROM `users` WHERE id = %s;", (user_id,))
    if not myCursor.fetchone():
        myCursor.close()
        connection.close()
        raise HTTPException(status_code = 404, detail = "Usuario no encontrado")

    query = """
        INSERT INTO `playlists` (user_id, name, description)
        VALUES (%s, %s, %s);
    """
    myCursor.execute(query, (user_id, playlist.name, playlist.description))
    connection.commit()
    new_playlist_id = myCursor.lastrowid

    myCursor.close()
    connection.close()

    return JSONResponse(
        content = {
            "message": "Playlist created successfully",
            "playlist_id": new_playlist_id,
        },
        status_code = 201,
    )


@app.delete("/playlists/{playlist_id}", tags = ["Playlists"], summary = "Eliminar una playlist")
def delete_playlist(playlist_id: int):
    connection = get_db()
    myCursor = connection.cursor()

    myCursor.execute("DELETE FROM `playlists` WHERE id = %s;", (playlist_id,))
    connection.commit()
    affected = myCursor.rowcount

    myCursor.close()
    connection.close()

    if affected == 0:
        raise HTTPException(status_code = 404, detail = "Playlist no encontrada")

    return JSONResponse(
        content = {"message": "Playlist deleted successfully"},
        status_code = 200,
    )


@app.post("/playlists/{playlist_id}/items", tags = ["Playlists"], summary = "Añadir un vídeo a una playlist")
def add_video_to_playlist(playlist_id: int, item: PlaylistItemCreate):
    video_data = get_video_by_id(item.twitch_video_id, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
    if "error" in video_data:
        raise HTTPException(status_code = 404, detail = video_data["error"])

    connection = get_db()
    myCursor = connection.cursor()

    myCursor.execute("SELECT id FROM `playlists` WHERE id = %s;", (playlist_id,))
    if not myCursor.fetchone():
        myCursor.close()
        connection.close()
        raise HTTPException(status_code = 404, detail = "Playlist no encontrada")

    query = """
        INSERT INTO `playlist_items` (playlist_id, twitch_video_id, video_title, streamer_login, video_url)
        VALUES (%s, %s, %s, %s, %s);
    """
    values = (
        playlist_id,
        video_data["twitch_video_id"],
        video_data["title"],
        video_data["streamer_login"],
        video_data["url"],
    )
    try:
        myCursor.execute(query, values)
        connection.commit()
    except Error:
        connection.rollback()
        raise HTTPException(status_code = 400, detail = "El vídeo ya está en esta playlist")
    finally:
        myCursor.close()
        connection.close()

    return JSONResponse(
        content = {"message": f"Video '{video_data['title']}' added to playlist"},
        status_code = 201,
    )


@app.delete(
    "/playlists/{playlist_id}/items/{twitch_video_id}",
    tags = ["Playlists"],
    summary = "Eliminar un vídeo de una playlist",
)
def remove_video_from_playlist(playlist_id: int, twitch_video_id: str):
    connection = get_db()
    myCursor = connection.cursor()

    myCursor.execute("SELECT id FROM `playlists` WHERE id = %s;", (playlist_id,))
    if not myCursor.fetchone():
        myCursor.close()
        connection.close()
        raise HTTPException(status_code = 404, detail = "Playlist no encontrada")

    myCursor.execute(
        "DELETE FROM `playlist_items` WHERE playlist_id = %s AND twitch_video_id = %s;",
        (playlist_id, twitch_video_id),
    )
    connection.commit()
    affected = myCursor.rowcount

    myCursor.close()
    connection.close()

    if affected == 0:
        raise HTTPException(status_code = 404, detail = "Vídeo no encontrado en esta playlist")

    return JSONResponse(
        content = {"message": "Video removed from playlist successfully"},
        status_code = 200,
    )