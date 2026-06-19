import pymupdf as pt
def extract_Text(raw):
    doc=pt.open(stream=raw,filetype="pdf")
    text=""
    for page in doc:
        text+=page.get_text()
    doc.close()
    return text