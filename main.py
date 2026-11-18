import os
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

app = FastAPI()

usuarios_db = [
    {
        "id": 1,
        "usuario": "asier3",
        "nombre": "Asier",
        "primer_apellido": "Aldekoa",
        "segundo_apellido": "Bengoetxea",
        "email": "asier@gmail.com",
        "artistas_favoritos": ["Fito & Fitipaldis", "Melendi"],
        "generos_favoritos": ["Pop", "Punk", "Rock"]
    },
    {
        "id": 2,
        "usuario": "jone4",
        "nombre": "Jone",
        "primer_apellido": "Muñoz",
        "segundo_apellido": "",
        "email": "jone@gmail.com",
        "artistas_favoritos": ["Guitarrica de la Fuente", "Niña Polaca"],
        "generos_favoritos": ["Pop"]
    }
]

@app.get("/")
def root():
    return {"message": "Hola Mundo!"}

@app.get("/users")
def get_users():
    return usuarios_db