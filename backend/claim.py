from encoder import encoder
from transformers import pipeline

nli=pipeline("text-classification",model="cross-encoder/nli-deberta-v3-small")

def checkClaim(chunks, claim):
    pairs = [{"text": c, "text_pair": claim} for c in chunks]
    score = nli(pairs)
    print(score)
    return score