#best matching 25 ; IMPROVED version of TF-IDF term frequency inverse document frequency

# BM25 uses 3 components: Term frequency , Inverse document frequency , document length normalization owever, BM25 introduces a saturation effect i.e beyond a certain point, additional occurrences of a term contribute less to the score. This prevents overly long documents from being unfairly favored.
#Inverse document frequency measures the importance of a term across the entire corpus. Rare terms are considered more informative than common ones
#BM25 accounts for document length by normalizing scores to prevent longer documents from dominating the rankings. This is controlled by the parameter 
#b which adjusts the influence of document length relative to the average document length (avgdl).
#stemmer makes words like run running runs to be roughly the same 
import bm25s
import Stemmer

def bm(chunks, query):
    res = chunks["documents"][0]
    stem = Stemmer.Stemmer("english")

    # tokenize corpus + query together so they share one vocab
    all_tokens = bm25s.tokenize(res + [query], stopwords="en", stemmer=stem)

    corpus_tokens = bm25s.tokenization.Tokenized(ids=all_tokens.ids[:-1], vocab=all_tokens.vocab)
    query_tokens = bm25s.tokenization.Tokenized(ids=[all_tokens.ids[-1]], vocab=all_tokens.vocab)

    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    x = min(10, len(res))
    results, scores = retriever.retrieve(query_tokens, k=x)

    return {
        'documents': [[chunks['documents'][0][i] for i in results[0]]],
        'metadatas': [[chunks['metadatas'][0][i] for i in results[0]]]
    }