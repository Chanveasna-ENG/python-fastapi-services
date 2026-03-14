# main.py

import os
import re
import httpx
import requests
from fastapi import FastAPI, Response, HTTPException
from my_types import SpeechRequest, ExtractTextRequest, SplitTextRequest
from utils import html2text, pdf2text


app = FastAPI(title="Python-FastAPI-Services")

@app.get("/")
def read_root():
    return {"status": "online", "message": "Services are running!!!"}


@app.post("/read")
def generate_speech(request: SpeechRequest): # Use the model here
    KOKORO_SERVICE_URL = os.getenv("KOKORO_URL")
    
    if not KOKORO_SERVICE_URL:
        raise HTTPException(status_code=500, detail=str("KOKORO_URL is missing."))

    response = requests.post(KOKORO_SERVICE_URL, json={
        "model": "kokoro",
        "input": request.text,
        "voice": request.voice
    })
    
    return Response(content=response.content, media_type="audio/mpeg")


@app.post("/extract-text")
async def read_from_file(request: ExtractTextRequest):
    url = request.file_url
    file_type = request.file_type
    
    try:
        # 1. Download the target file/webpage
        async with httpx.AsyncClient() as client:
            # Add headers to bypass basic bot-protection on news sites
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            
        content = ""

        if file_type == "text/plain":
            content = response.text
            
        elif file_type == "link":
            content = html2text(response.text)

        elif file_type == "application/pdf":
            content = pdf2text(response.content)
                    
        else:
            raise HTTPException(status_code=400, detail="Unsupported file_type provided.")
            
        return Response(content=content, media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/split-text")
def get_text_chunks(request: SplitTextRequest):
    
    text = request.text 
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= request.text_length:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return {"chunks": chunks}