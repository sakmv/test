import chromadb
from input import insert_file
from visual import visualize
from retrieve import retrieve
from text_splitter import text_splitter
from groq import getPrompt
from fastapi import FastAPI, UploadFile , File
from pydantic import BaseModel

app=FastAPI()


client = chromadb.Client()
collection = client.create_collection(name="intern-RAG")
splitter=text_splitter()
class Query(BaseModel):
    text:str

@app.post("/upload")
async def upload_f(file:UploadFile=File(...)):
    text=await file.read()
    insert_file(text,collection)
    

@app.post("/query")
async def query_res(query:Query):
    txt=query.text
    result=getPrompt(txt,retrieve(txt,collection))
    return {'response':result}



# print("enter your filepaths.Type done to stop \n")
# while True:
#     file=input("PATH: ")
#     if file=='done':
#          break
#     insert_file(str(file),collection)

# print("enter your question. Type done to exit \n")
# while True:
#      query=input("ques: ")
#      if query=="done":
#           break
#      retrieved=retrieve(query,collection)
#      getPrompt(query,retrieved['documents'])

# data=collection.get(include=["documents","embeddings"])
# visualize(data["documents"],data["embeddings"])
