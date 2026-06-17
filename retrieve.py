from encoder import get_embedding
def retrieve(u_query,collection):
    embedding = get_embedding(u_query)
    return collection.query(query_embeddings=[embedding],n_results=3)

#n_results is top n results
#query_texts takes a string of queries as input