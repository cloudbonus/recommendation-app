import matplotlib.pyplot as plt
from gensim import models, corpora
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

lsi = models.LsiModel.load('model_data/lsi_model')
corpus = corpora.MmCorpus('model_data/corpus')

data = []
for doc in corpus:
    vec = lsi[doc]
    data.append([x[1] for x in vec])

scaler = StandardScaler()
data_std = scaler.fit_transform(data)

pca = PCA(n_components=2)

pca_data = pca.fit_transform(data_std)

plt.scatter(pca_data[:, 0], pca_data[:, 1])
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.show()