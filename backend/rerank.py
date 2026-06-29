from encoder import encoder
from sentence_transformers import CrossEncoder
import numpy as np
mode=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
def reranker(chunks, query, top_k=3):
    c = chunks["documents"]
    data=c[0]
 
    pairs = [(query, chunk) for chunk in data]
   
    scores = mode.predict(pairs)
#enumurate scors makes it(original index,score) pair then we take the top k and then use those original indices to get the metadata and docs
    ranked= sorted(enumerate(scores),key= lambda x:x[1],reverse=True)
    top=[i for i,score in ranked[:top_k]] 
    print(scores)

    return {
        'documents':[[chunks["documents"][0][i] for i in top]],
        'metadatas':[[chunks["metadatas"][0][i] for i in top]]
        }
