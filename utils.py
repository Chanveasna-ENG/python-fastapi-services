from google import genai
from google.genai import types
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from config import prompt


client = genai.Client()

def gemini_ocr(doc):
    content_part = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        
        ocr_response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=[
                types.Part.from_text(text=prompt),
                types.Part.from_bytes(data=img_bytes, mime_type="image/png")
            ]
        )
        if ocr_response.text != None:
            content_part.append(ocr_response.text)
        
    return "\n".join(content_part)


def html2text(response):
    soup = BeautifulSoup(response, "html.parser")
    for noisy_element in soup(["script", "style", "nav", "header", "footer", "aside"]):
        noisy_element.extract()
    content = soup.get_text(separator='\n', strip=True)
    
    return content


def pdf2text(response):
    content = ""
    doc = fitz.open(stream=response, filetype="pdf")
    
    for page in doc:
        content += page.get_text("text").strip() + "\n"

    # OCR Fallback
    if len(content.strip()) < (50 * len(doc)):
        content = gemini_ocr(doc)
    return content