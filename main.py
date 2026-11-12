import os
import requests
import mysql.connector
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException

load_dotenv()
GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

app = FastAPI()

# 1. Ruta raíz (prueba)
@app.get("/")
def root():
    return {"message": "Hola Mundo"}