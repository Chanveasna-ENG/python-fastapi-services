# main.py

import os
import re
import httpx
import requests
from fastapi import FastAPI, Response, HTTPException
from my_types import SpeechRequest, ExtractTextRequest, SplitTextRequest
from utils import html2text, pdf2text
from validator import is_safe_url


app = FastAPI(title="Python-FastAPI-Services")

@app.get("/")
def read_root():
    return {"status": "online", "message": "Services are running!!!"}


@app.post(
    "/read",
    responses={
        500: {"description": "Internal server error, specifically KOKORO_URL is missing."},
    }
)
def generate_speech(request: SpeechRequest): # Use the model here
    KOKORO_SERVICE_URL = os.getenv("KOKORO_URL")
    
    if not KOKORO_SERVICE_URL:
        raise HTTPException(status_code=500, detail=str("KOKORO_URL is missing."))

    response = requests.post(KOKORO_SERVICE_URL, json={
        "model": "kokoro",
        "input": request.text,
        "voice": "jf_alpha" if request.language == "jp" else "bf_emma" 
    })
    
    return Response(content=response.content, media_type="audio/mpeg")


@app.post(
    "/extract-text",
    responses={
        400: {"description": "Unsupported file_type."},
        403: {"description": "SSRF Protection: URL or Redirect blocked."},
        500: {"description": "Internal server error."},
        502: {"description": "Upstream website returned an error."}
    }
)
async def read_from_file(request: ExtractTextRequest):
    url = request.file_url
    file_type = request.file_type
    
    if not is_safe_url(url):
         raise HTTPException(status_code=403, detail="Initial URL blocked by SSRF protection.")

    try:
        async with httpx.AsyncClient() as client:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            
            # 1. Disable auto-redirects to prevent bypass
            response = await client.get(url, headers=headers, follow_redirects=False)

            # 2. Manual Redirect Validation (up to N redirects)
            max_redirects = 5
            for _ in range(max_redirects):
                if not response.is_redirect:
                    break
                redirect_url = response.headers.get("Location")
                # Resolve relative URLs against the current request URL
                redirect_url = str(response.url.join(redirect_url))
                if not is_safe_url(redirect_url):
                    raise HTTPException(status_code=403, detail="Redirect blocked by SSRF protection.")
                response = await client.get(redirect_url, headers=headers, follow_redirects=False)
            else:
                raise HTTPException(status_code=400, detail="Too many redirects.")

            response.raise_for_status()
            
        content = ""
        if file_type == "text/plain":
            content = response.text
        elif file_type == "url":
            content = html2text(response.text)
        elif file_type == "application/pdf":
            content = pdf2text(response.content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file_type.")
            
        return Response(content=content, media_type="text/plain")
        
    # FIX: Allow our specific HTTPExceptions (400, 403) to pass through
    except HTTPException:
        raise
    # FIX: Catch httpx specific errors and return 502
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream request failed.")
    # FIX: Everything else is a 500
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected extraction error.")


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
