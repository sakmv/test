import chromadb
from input import insert_file
from visual import visualize
from retrieve import retrieve
from groq import getPrompt
from fastapi import FastAPI, UploadFile , File
from pydantic import BaseModel
from pdf_text import extract_Text
##SINCE OUR BACKEND WILL BE ON RENDER AND FRONTEND ON VERCEL WE NEED CORS(CROSS ORIGIN RESOURCE SHARING)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = chromadb.Client()
collection = client.create_collection(name="intern-RAG")
class Query(BaseModel):
    text:str

@app.post("/upload")
async def upload_f(file:UploadFile=File(...)):
    raw=await file.read()
    if file.filename.endswith(".pdf"):
        text = extract_Text(raw)
    else:
        text = raw.decode("utf-8")
    insert_file(text,collection,file.filename)
    return {"status":"success","filename":file.filename}
    

@app.post("/query")
async def query_res(query:Query):
    txt=query.text
    result=getPrompt(txt,retrieve(txt,collection))
    return {'response':result}

@app.get("/visual")
async def visualise():
    data=collection.get(include=["documents","embeddings"])##this return numpy ndarry so if every directly returning it need to convert to list because not json native
    sim_mat=visualize(data["documents"],data["embeddings"])
    return{
        "documents":data["documents"],
        "matrix":sim_mat
    }

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

