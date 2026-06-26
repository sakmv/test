def dupes(docs:list,meta:list):
    seen=set()
    visited_docs = []
    visited_meta=[]
    for doc,m in zip(docs,meta):
        if(doc not in seen):
            visited_docs.append(doc)
            visited_meta.append(m)
            seen.add(doc)
    return visited_docs,visited_meta

    
