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
from fastapi.responses import StreamingResponse
import json
from rerank import reranker
from bm25 import bm
from dedupe import dupes
from claim import checkClaim

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

@app.post("/files")
async def getFiles(session:Session):
    fileSet=set()
    collection=getCollection(session.ses)
    data=collection.get(include=["metadatas"])
    print("DATA:", data)  
    for d in data["metadatas"]:
        fileSet.add(d["source"])
    return {
        "fileSet":list(fileSet)
    }


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
async def query_res(query: Query):
    txt = query.text
    collection = getCollection(query.sessionid)
    retrieved = retrieve(txt, collection)
    bms=bm(retrieved,txt)

    docs,meta=dupes(retrieved["documents"][0]+bms["documents"][0],retrieved["metadatas"][0]+bms["metadatas"][0])

    merged={"documents":[docs],
            "metadatas":[meta]}

    reranked=reranker(merged,txt)
    print("RETRIEVED---")
    print(retrieved)
    print("RERANKED----")
    print(reranked)
    print('BMS---')
    print(bms)
    def event_stream():
        full_response = ""
        for token in getPrompt(txt, reranked, query.memory):
            full_response += token
            yield f"data: {json.dumps({'token': token, 'type': 'answer'})}\n\n"
        for token in getSource(full_response, reranked):
            yield f"data: {json.dumps({'token': token, 'type': 'source'})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.post("/visual")
async def visualise(sesh:Session):
    collection=getCollection(sesh.ses)
    data=collection.get(include=["documents","embeddings"])##this return numpy ndarry so if every directly returning it need to convert to list because not json native
    emat,pca_points=visualize(data["documents"])
    return{
        "documents":data["documents"],
        "matt":emat,
        "pca":pca_points
    }

@app.post("/claim")
async def claims(query:Query):
    entailment=[]
    neutral=[]
    contradiction=[]
    txt = query.text
    collection = getCollection(query.sessionid)
    retrieved = retrieve(txt, collection)
    bms=bm(retrieved,txt)
    docs,meta=dupes(retrieved["documents"][0]+bms["documents"][0],retrieved["metadatas"][0]+bms["metadatas"][0])
    merged={"documents":[docs],
            "metadatas":[meta]}
    reranked=reranker(merged,txt)
    print(reranked)
    score= checkClaim(reranked["documents"],txt)
    for i,s in enumerate(score):
        if (s[0]["label"]=="entailment") and (s[0]["score"] > 0.5) :
            entailment.append((reranked["documents"][i],s[0]["score"]))
        elif (s[0]["label"]=="contradiction") and (s[0]["score"] > 0.5):
            contradiction.append((reranked["documents"][i],s))
        elif (s[0]["label"]=="neutral") and (s[0]["score"] > 0.5):
            neutral.append((reranked["documents"][i],s))
    if entailment:
        best=max(entailment,key=lambda x:x[1])
        return {
            "label":"entailment","documents":best[0]
        }
    elif contradiction:
        best=max(contradiction,key=lambda x:x[1])
        return {
            "label":"contradiction","documents":best[0]
        } 
    if neutral:
        best=max(neutral,key=lambda x:x[1])
        return {
            "label":"neutral","documents":best[0]
        }

    

