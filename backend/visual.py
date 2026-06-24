from text_splitter import text_splitter
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer
def visualize(chunks):
#similarity matrix
    transformer=SentenceTransformer('all-MiniLM-L6-v2')
    embed=transformer.encode(chunks)
    em_mat=np.ones((len(chunks), len(chunks)))
    for i in range(len(chunks)):
        for j in range(len(chunks)):
                em_mat[i][j]=np.dot(embed[i],embed[j])
##interactive plot using plotly
#     fig=px.imshow(em_mat,color_continuous_scale='magma')
#     fig.update_layout(title="Similarity Matrix of generated chunks")
#     fig.update_coloraxes(colorbar_title="Cosine Similarity")
#     fig.show()
# #dimensionality reduced to 2 for display on a scatter plot graph 
    pca = PCA(n_components=2)
    loc = pca.fit_transform(embed)  

    pca_points = [{"x": float(x), "y": float(y), "label": f"chunk {i}"} 
                  for i, (x, y) in enumerate(loc)]
    
    return em_mat.tolist(), pca_points


#MATPLOTLIB HEATMAP
# plt.imshow(em_mat,cmap='magma',interpolation='nearest')
# plt.colorbar()
# plt.title("Similarity Matrix of generated chunks")
# plt.show()
