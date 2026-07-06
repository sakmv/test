import os
os.environ['HF_TOKEN']=""

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
from text_splitter import text_splitter
from fastapi.responses import Response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = chromadb.Client()
  
def getCorpus(collection):
    result = collection.get(include=["documents", "metadatas"])
    return {
        "documents": [result["documents"]],
        "metadatas": [result["metadatas"]]
    }
def getCollection(sesh:str):
    return client.get_or_create_collection(name=sesh)

class Delete(BaseModel):
    ses:str
    file:str

class Query(BaseModel):
    text:str
    sessionid:str
    memory:list

class Session(BaseModel):
    ses:str

class Memory(BaseModel):
    res:list

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
    print(retrieved)
    print("\n \n \n")
    all = getCorpus(collection) 
    bms=bm(all,txt)
    print(bms)
    docs,meta=dupes(retrieved["documents"][0]+bms["documents"][0],retrieved["metadatas"][0]+bms["metadatas"][0])

    merged={"documents":[docs],
            "metadatas":[meta]}

    reranked=reranker(merged,txt)
    print("\n \n RERANKED:   \n",reranked)
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
@app.post("/download")
async def download(mem: Memory):
    response_list = mem.res

    lines = ["NoteMind - Session Export\n"]
    for i, entry in enumerate(response_list, 1):
        lines.append(f"Entry {i:02d}")
        lines.append(f"Query: {entry.get('query', '')}")
        lines.append(f"Response: {entry.get('response', '')}")
        lines.append("-" * 40)
        lines.append("")

    content = "\n".join(lines)

    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=notemind_session.txt"}
    )
@app.post("/arena")
async def arena(query: Query):
    txt = query.text
    collection = getCollection(query.sessionid)

    retrieved = retrieve(txt, collection,5)          
    full_corpus = getCorpus(collection)   
    bms = bm(full_corpus, txt)                       

    docs, meta = dupes(
        retrieved["documents"][0] + bms["documents"][0],
        retrieved["metadatas"][0] + bms["metadatas"][0]
    )
    merged = {"documents": [docs], "metadatas": [meta]}
    reranked = reranker(merged, txt, top_k=3)        

    return {
        "encoder": {
            "documents": retrieved["documents"][0][:3],
            "metadatas": retrieved["metadatas"][0][:3]
        },
        "bm25": {
            "documents": bms["documents"][0][:3],
            "metadatas": bms["metadatas"][0][:3]
        },
        "reranked": {
            "documents": reranked["documents"][0][:3],
            "metadatas": reranked["metadatas"][0][:3]
        }
    }

@app.delete("/delete")
async def dele(sesh:Delete):
    collection=getCollection(sesh.ses)
    collection.delete(
	where={"source": f"{sesh.file}"}
)
    return {"status":"deleted","file":sesh.file}




# CLAIM VERIFICATION --SCRAPPED
# @app.post("/claim")
# async def claims(query: Query):
#     entailment = []
#     neutral = []
#     contradiction = []
#     txt = query.text
#     collection = getCollection(query.sessionid)
#     retrieved = retrieve(txt, collection)
#     bms = bm(retrieved, txt)
#     docs, meta = dupes(
#         retrieved["documents"][0] + bms["documents"][0],
#         retrieved["metadatas"][0] + bms["metadatas"][0]
#     )
#     merged = {"documents": [docs], "metadatas": [meta]}
#     reranked = reranker(merged, txt)

#     splitter = text_splitter()

#     chunks = []
#     print("TOP 1 CHUNK")
#     print(reranked["documents"][0])
#     print("----EOF TOP 1 CHUNKS")
#     for doc in reranked["documents"][0]:
#         chunks.extend(splitter.rec_chunk(doc, 300, 50))
#     print(chunks)
#     score = checkClaim(chunks, txt)
#     print("THESE ARE THE SCORES : ",score)
#     for i, s in enumerate(score):
#         label = s["label"]
#         conf = s["score"]
#         if conf <= 0.9:
#             continue
#         if label == "entailment":
#             entailment.append((chunks[i], conf))
#         elif label == "contradiction":
#             contradiction.append((chunks[i], conf))
#         elif label == "neutral":
#             neutral.append((chunks[i], conf))

#     if entailment:
#         best = max(entailment, key=lambda x: x[1])
#         return {"label": "entailment", "documents": best[0]}
#     elif contradiction:
#         best = max(contradiction, key=lambda x: x[1])
#         return {"label": "contradiction", "documents": best[0]}
#     elif neutral:
#         best = max(neutral, key=lambda x: x[1])
#         return {"label": "neutral", "documents": None}

#     return {"label": "neutral", "documents": None}

    

