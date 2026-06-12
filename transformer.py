from text_splitter import text_splitter
from sentence_transformers import SentenceTransformer

with open("input.txt", "r") as f:
    text=f.read()

#chunking
splitter=text_splitter()
chunks=splitter.rec_chunk(text,500,50)

#embedding
embed_model=SentenceTransformer("all-MiniLM-L6-v2")
embed=embed_model.encode(chunks)

