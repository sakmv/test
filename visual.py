from text_splitter import text_splitter
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.decomposition import PCA

def visualize(chunks,embed):
#similarity matrix
    em_mat=np.ones((len(chunks), len(chunks)))
    for i in range(len(chunks)):
        for j in range(len(chunks)):
            if i!=j:
                em_mat[i][j]=np.dot(embed[i],embed[j])

##interactive plot using plotly
    fig=px.imshow(em_mat,color_continuous_scale='magma')
    fig.update_layout(title="Similarity Matrix of generated chunks")
    fig.update_coloraxes(colorbar_title="Cosine Similarity")
    fig.show()
#dimensionality reduced to 2 for display on a scatter plot graph 
    pca = PCA(n_components=2)
    loc = pca.fit_transform(embed)  

    plt.figure(figsize=(8, 6))
    for i, (x, y) in enumerate(loc):
         plt.scatter(x, y)
         plt.annotate(f"chunk {i}", (x, y), fontsize=8)
    plt.title("Chunk embeddings in 2D (PCA)")
    plt.show()


#MATPLOTLIB HEATMAP
# plt.imshow(em_mat,cmap='magma',interpolation='nearest')
# plt.colorbar()
# plt.title("Similarity Matrix of generated chunks")
# plt.show()
