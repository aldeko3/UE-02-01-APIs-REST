import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hola Mundo!"}

def get_twitch_token() -> str:
    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    response = requests.post(url, data=payload, timeout=10)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="No se pudo obtener el token de Twitch")

    token_json = response.json()
    return token_json["access_token"]