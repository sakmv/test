import uuid
from text_splitter import text_splitter
from encoder import get_embedding
def insert_file(text:str,collection,file:str):
    splitter=text_splitter()
    chunks=splitter.rec_chunk(text,600,70)
    embeddings = [get_embedding(chunk) for chunk in chunks]
    collection.add(documents=chunks,embeddings=embeddings,ids=[str(uuid.uuid4()) for _ in range(len(chunks))],metadatas=[{"source":f"{file}"} for _ in range(len(chunks))])
