from text_splitter import text_splitter
from sentence_transformers import SentenceTransformer
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

print("Enter ur query:")
user_query = input()
with open("input.txt", "r",encoding="utf-8") as f:
    text=f.read()

#chunking
splitter=text_splitter()
chunks=splitter.rec_chunk(text,200,50)
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
# plt.imshow(em_mat,cmap='magma',interpolation='nearest')
# plt.colorbar()
# plt.title("Similarity Matrix of generated chunks")
# plt.show()

for idx,chunk in enumerate(chunks):
    print(f"Chunk {idx+1}: {chunk}\n")

##interactive plot using plotly
fig=px.imshow(em_mat,color_continuous_scale='magma')
fig.update_layout(title="Similarity Matrix of generated chunks")
fig.update_coloraxes(colorbar_title="Cosine Similarity")
fig.show()


from sklearn.decomposition import PCA


pca = PCA(n_components=2)
coords = pca.fit_transform(embed)  # embed shape (n_chunks, 384) → (n_chunks, 2)

plt.figure(figsize=(8, 6))
for i, (x, y) in enumerate(coords):
    plt.scatter(x, y)
    plt.annotate(f"chunk {i}", (x, y), fontsize=8)
plt.title("Chunk embeddings in 2D (PCA)")
plt.show()