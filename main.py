import chromadb
from input import insert_file
from visual import visualize
from retrieve import retrieve
from text_splitter import text_splitter

client = chromadb.Client()
collection = client.create_collection(name="intern-RAG")
print("enter your filepaths.Type done to stop \n")
while True:
    file=input("PATH: ")
    if file=='done':
         break
    insert_file(str(file),collection)
    
print("enter your question. Type done to exit \n")
while True:
     query=input("ques: ")
     if query=="done":
          break
     retrieved=retrieve(query,collection)
     print(retrieved)

data=collection.get(include=["documents","embeddings"])
visualize(data["documents"],data["embeddings"])
