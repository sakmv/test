from text_splitter import text_splitter
from sentence_transformers import SentenceTransformer
import numpy as np
import matplotlib.pyplot as plt
print("Enter ur query:")
user_query = input()
with open("input.txt", "r",encoding="utf-8") as f:
    text=f.read()

#chunking
splitter=text_splitter()
chunks=splitter.rec_chunk(text,500,1)
#embedding
embed_model=SentenceTransformer("all-MiniLM-L6-v2")
embed=embed_model.encode(chunks)
user_embed=embed_model.encode(user_query)

em_mat=np.ones((len(chunks), len(chunks)))
for i in range(len(chunks)):
    for j in range(len(chunks)):
        if i!=j:
            em_mat[i][j]=np.dot(embed[i],embed[j])
sim=np.array([np.dot(user_embed,embed[i]) for i in range(len(chunks))])
print(chunks[np.argmax(sim)])
plt.imshow(em_mat,cmap='magma',interpolation='nearest')

plt.show()

