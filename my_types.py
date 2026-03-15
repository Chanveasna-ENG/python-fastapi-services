from pydantic import BaseModel

class SpeechRequest(BaseModel):
    text: str
    language: str = "en"

class ExtractTextRequest(BaseModel):
    file_url: str
    file_type: str = "text/plain"

class SplitTextRequest(BaseModel):
    text: str
    text_length: int = 3000