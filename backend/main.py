import chromadb
from input import insert_file
from visual import visualize
from retrieve import retrieve
from groq import getPrompt,getSource
from fastapi import FastAPI, UploadFile , File , Form
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
def getCollection(sesh:str):
    return client.get_or_create_collection(name=sesh)
class Query(BaseModel):
    text:str
    sessionid:str
    memory:list

class Session(BaseModel):
    ses:str

@app.post("/upload")
async def upload_f(file:list[UploadFile]=File(...),sessionid:str=Form(...)):
    filenames=[]
    for f in file:
        raw=await f.read()
        if f.filename.endswith(".pdf"):
            text = extract_Text(raw)
        else:
            text = raw.decode("utf-8")
        collection=getCollection(str(sessionid))
        insert_file(text,collection,f.filename)
        filenames.append(f.filename)
    return {"status":"success","filename":filenames}
    

@app.post("/query")
async def query_res(query:Query):
    txt=query.text
    collection=getCollection(query.sessionid)
    retrieved = retrieve(txt, collection)
    print("RETRIEVED CHUNKS:", retrieved['documents'])
    result=getPrompt(txt,retrieved,query.memory)
    source=getSource(result,retrieved)
    return {'response':result,'sources':source}

@app.post("/visual")
async def visualise(sesh:Session):
    collection=getCollection(sesh.ses)
    data=collection.get(include=["documents","embeddings"])##this return numpy ndarry so if every directly returning it need to convert to list because not json native
    sim_mat=visualize(data["documents"],data["embeddings"])
    return{
        "documents":data["documents"],
        "matrix":sim_mat
    }
