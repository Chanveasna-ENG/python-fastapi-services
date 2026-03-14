# main.py

from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="Python-FastAPI-Services")

class SpeechRequest(BaseModel):
    text: str
    voice: str = "bf_emma"


@app.get("/")
def read_root():
    return {"status": "online", "message": "Services are running!!!"}


# A wrapper for Kokoro
@app.post("/read")
def generate_speech(request: SpeechRequest): # Use the model here
    KOKORO_SERVICE_URL = os.getenv("KOKORO_URL")
    
    # Access data via request.text and request.voice
    response = requests.post(KOKORO_SERVICE_URL, json={
        "model": "kokoro",
        "input": request.text,
        "voice": request.voice
    })
    
    return Response(content=response.content, media_type="audio/mpeg")