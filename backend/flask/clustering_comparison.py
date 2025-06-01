from model import get_combined_features
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering, DBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt

# 1. Get combined feature strings for all profiles
combined_features = get_combined_features()
tfidf = TfidfVectorizer(max_features=100)
X = tfidf.fit_transform(combined_features)

# 2. Automatically select the best K for KMeans and Agglomerative using silhouette score
def find_best_k(X, algo_class, k_range=range(2, 11)):
    best_k = None
    best_score = -1
    best_labels = None
    scores = []
    for k in k_range:
        if algo_class == SpectralClustering:
            algo = algo_class(n_clusters=k, affinity='nearest_neighbors', random_state=42, assign_labels='kmeans')
            labels = algo.fit_predict(X.toarray())
        else:
            algo = algo_class(n_clusters=k)
            labels = algo.fit_predict(X if algo_class != AgglomerativeClustering else X.toarray())
        if len(set(labels)) < 2:  # avoid trivial solutions
            scores.append(-1)
            continue
        score = silhouette_score(X, labels)
        scores.append(score)
        if score > best_score:
            best_score = score
            best_k = k
            best_labels = labels
    return best_k, best_score, best_labels, scores

# Find best K for KMeans
kmeans_best_k, kmeans_best_score, kmeans_labels, kmeans_scores = find_best_k(X, KMeans)
# Find best K for Agglomerative
agglo_best_k, agglo_best_score, agglo_labels, agglo_scores = find_best_k(X, AgglomerativeClustering)
# Find best K for Spectral
spectral_best_k, spectral_best_score, spectral_labels, spectral_scores = find_best_k(X, SpectralClustering)

# 3. DBSCAN does not require K
dbscan_algo = DBSCAN(eps=0.5, min_samples=5)
dbscan_labels = dbscan_algo.fit_predict(X)
# Remove noise points for metrics (-1 label)
dbscan_valid = dbscan_labels != -1
if dbscan_valid.sum() > 1:
    dbscan_silhouette = silhouette_score(X[dbscan_valid], dbscan_labels[dbscan_valid])
    dbscan_ch = calinski_harabasz_score(X[dbscan_valid].toarray(), dbscan_labels[dbscan_valid])
    dbscan_db = davies_bouldin_score(X[dbscan_valid].toarray(), dbscan_labels[dbscan_valid])
    dbscan_n_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
else:
    dbscan_silhouette = dbscan_ch = dbscan_db = None
    dbscan_n_clusters = 0

# 4. Collect and print results
results = {
    'KMeans': {
        'best_k': kmeans_best_k,
        'silhouette': kmeans_best_score,
        'calinski_harabasz': calinski_harabasz_score(X.toarray(), kmeans_labels),
        'davies_bouldin': davies_bouldin_score(X.toarray(), kmeans_labels),
        'n_clusters': len(set(kmeans_labels))
    },
    'Agglomerative': {
        'best_k': agglo_best_k,
        'silhouette': agglo_best_score,
        'calinski_harabasz': calinski_harabasz_score(X.toarray(), agglo_labels),
        'davies_bouldin': davies_bouldin_score(X.toarray(), agglo_labels),
        'n_clusters': len(set(agglo_labels))
    },
    'Spectral': {
        'best_k': spectral_best_k,
        'silhouette': spectral_best_score,
        'calinski_harabasz': calinski_harabasz_score(X.toarray(), spectral_labels),
        'davies_bouldin': davies_bouldin_score(X.toarray(), spectral_labels),
        'n_clusters': len(set(spectral_labels))
    },
    'DBSCAN': {
        'silhouette': dbscan_silhouette,
        'calinski_harabasz': dbscan_ch,
        'davies_bouldin': dbscan_db,
        'n_clusters': dbscan_n_clusters
    }
}

print("Comparison Results (Best K automatically selected):")
for algo, res in results.items():
    print(f"{algo}: {res}")
    

# Optional: plot silhouette scores for each algorithm
plt.figure(figsize=(10, 6))
plt.plot(range(2, 11), kmeans_scores, marker='o', label='KMeans')
plt.plot(range(2, 11), agglo_scores, marker='o', label='Agglomerative')
plt.plot(range(2, 11), spectral_scores, marker='o', label='Spectral')
plt.xlabel("Number of Clusters (K)")
plt.ylabel("Silhouette Score")
plt.title("Silhouette Score vs Number of Clusters")
plt.legend()
plt.tight_layout()
plt.savefig("silhouette_scores.png")
plt.show()