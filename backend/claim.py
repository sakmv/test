from encoder import encoder
from transformers import pipeline

nli=pipeline("text-classification",model="cross-encoder/nli-deberta-v3-small")

def checkClaim(chunks,claim):
    score=[]
    for c in chunks:
        score.append(nli(f"{c}[SEP]{claim}"))
    print(score)
    return score
