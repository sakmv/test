from encoder import encoder
from sentence_transformers import CrossEncoder
import numpy as np
mode=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
def reranker(chunks, query, top_k=3):
    c = chunks["documents"]
    data=c[0]
    print(data)
    pairs = [(query, chunk) for chunk in data]
    print(pairs)
    scores = mode.predict(pairs)
    print("SCORES--")
    print(scores)
    print(chunks)
    print("THIS IS THE ZIP")
    print(zip(chunks,scores))
    ranked_chunks = sorted(
        zip([chunks], scores),
        key=lambda x: x[1],
        reverse=True
    )
    print("RANKED---")
    print(ranked_chunks)
    return [chunk for chunk, score in ranked_chunks[:top_k]]
