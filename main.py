# main.py

from fastapi import FastAPI
import requests
import os

app = FastAPI(title="Python-FastAPI-Services")

KOKORO_SERVICE_URL = os.getenv("KOKORO_URL")

@app.get("/")
def read_root():
    return {"status": "online", "message": "Services are running!!!"}

# Example 1: A wrapper for Kokoro
@app.post("/read")
def say_hello(text: str, voice: str="bf_emma"):

    response = requests.post(KOKORO_SERVICE_URL, json={
        "model": "kokoro",
        "input": text,
        "voice": voice
    })
    return Response(content=kokoro_res.content, media_type="audio/mpeg")
