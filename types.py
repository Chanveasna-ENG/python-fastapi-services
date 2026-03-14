from pydantic import BaseModel

class SpeechRequest(BaseModel):
    text: str
    voice: str = "bf_emma"

class ExtractTextRequest(BaseModel):
    file_url: str
    file_type: str = "text/plain"