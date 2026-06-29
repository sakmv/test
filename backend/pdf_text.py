import pymupdf as pt
import pytesseract
from pdf2image import convert_from_bytes
def extract_Text(raw):
    doc=pt.open(stream=raw,filetype="pdf")
    text=""
    for i,page in enumerate(doc):
        buffer=''
        buffer=page.get_text()
        if(len(buffer)<50):
            images=convert_from_bytes(raw,dpi=300,first_page=i+1,last_page=i+1)
            buffer=pytesseract.image_to_string(images[0])
        text+=buffer+"\n\n"
    doc.close()
    return text