def retrieve(u_query,collection):
    return collection.query(query_texts=u_query,n_results=3)

#n_results is top n results
#query_texts takes a string of queries as input