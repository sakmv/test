import pymupdf as pt
import pytesseract
from pdf2image import convert_from_bytes
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Saksham Manu Verma\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
def extract_Text(raw):
    doc=pt.open(stream=raw,filetype="pdf")
    text=""
    for i,page in enumerate(doc):
        buffer=page.get_text()
        if(len(buffer.strip())<50):
            images=convert_from_bytes(raw,dpi=200,first_page=i+1,last_page=i+1,poppler_path=r"C:\Users\Saksham Manu Verma\pdf2image_poppler\poppler-26.02.0\Library\bin")
            buffer=pytesseract.image_to_string(images[0])
        text+=buffer+"\n\n"
    doc.close()
    return text