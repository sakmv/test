import uuid
from text_splitter import text_splitter
def insert_file(file,collection):
    with open(file,"r",encoding="utf-8") as f:
        text=f.read()
    splitter=text_splitter()
    chunks=splitter.rec_chunk(text,200,50)
    collection.add(documents=chunks,ids=[str(uuid.uuid4()) for _ in range(len(chunks))],metadatas=[{"source":f"{file} chunk_{i}"}for i in range(len(chunks))])
