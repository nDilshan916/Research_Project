from model import get_combined_features
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering, DBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import numpy as np

# 1. Get combined feature strings for all profiles
combined_features = get_combined_features()
tfidf = TfidfVectorizer(max_features=100)
X = tfidf.fit_transform(combined_features)

# 2. Elbow Method Implementation
def elbow_method(X, max_clusters=10):
    """Calculate WCSS (Within-Cluster Sum of Squares) for different K values"""
    wcss = []
    K_range = range(1, max_clusters + 1)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        wcss.append(kmeans.inertia_)
    
    return K_range, wcss

# 3. Find optimal K using elbow method
def find_elbow_point(wcss, K_range):
    """Find elbow point using the rate of change method"""
    # Calculate the rate of change
    diffs = np.diff(wcss)
    diff_ratios = np.diff(diffs)
    
    # Find the point where the rate of change starts to level off
    if len(diff_ratios) > 0:
        elbow_idx = np.argmax(diff_ratios) + 2  # +2 because of double diff
        return K_range[elbow_idx] if elbow_idx < len(K_range) else K_range[-1]
    return K_range[2]  # Default to 3 if calculation fails

# 4. Automatically select the best K for KMeans and Agglomerative using silhouette score
def find_best_k(X, algo_class, k_range=range(2, 11)):
    best_k = None
    best_score = -1
    best_labels = None
    scores = []
    wcss_values = []  # For elbow method (only applicable to KMeans)
    
    for k in k_range:
        if algo_class == SpectralClustering:
            algo = algo_class(n_clusters=k, affinity='nearest_neighbors', random_state=42, assign_labels='kmeans')
            labels = algo.fit_predict(X.toarray())
        elif algo_class == KMeans:
            algo = algo_class(n_clusters=k, random_state=42, n_init=10)
            algo.fit(X)
            labels = algo.labels_
            wcss_values.append(algo.inertia_)  # Store WCSS for elbow method
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
    
    return best_k, best_score, best_labels, scores, wcss_values

# 5. Calculate elbow method for KMeans
K_range, wcss = elbow_method(X, max_clusters=10)
elbow_k = find_elbow_point(wcss, list(K_range))

print(f"Elbow Method suggests optimal K: {elbow_k}")

# Find best K for each algorithm
kmeans_best_k, kmeans_best_score, kmeans_labels, kmeans_scores, kmeans_wcss = find_best_k(X, KMeans)
agglo_best_k, agglo_best_score, agglo_labels, agglo_scores, _ = find_best_k(X, AgglomerativeClustering)
spectral_best_k, spectral_best_score, spectral_labels, spectral_scores, _ = find_best_k(X, SpectralClustering)

# 6. DBSCAN does not require K
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

# 7. Collect and print results
results = {
    'KMeans': {
        'best_k_silhouette': kmeans_best_k,
        'best_k_elbow': elbow_k,
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

print("\nComparison Results (Best K automatically selected):")
print(f"Elbow Method suggests K = {elbow_k} for KMeans")
print("-" * 60)
for algo, res in results.items():
    print(f"{algo}: {res}")

# 8. Create comprehensive plots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

# Plot 1: Elbow Method
ax1.plot(K_range, wcss, 'bo-', linewidth=2, markersize=8)
ax1.axvline(x=elbow_k, color='red', linestyle='--', linewidth=2, 
           label=f'Elbow at K={elbow_k}')
ax1.set_xlabel('Number of Clusters (K)')
ax1.set_ylabel('Within-Cluster Sum of Squares (WCSS)')
ax1.set_title('Elbow Method for Optimal K (KMeans)')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Plot 2: Silhouette Scores
ax2.plot(range(2, 11), kmeans_scores, marker='o', label='KMeans', linewidth=2)
ax2.plot(range(2, 11), agglo_scores, marker='s', label='Agglomerative', linewidth=2)
ax2.plot(range(2, 11), spectral_scores, marker='^', label='Spectral', linewidth=2)
ax2.axvline(x=elbow_k, color='red', linestyle='--', alpha=0.7, 
           label=f'Elbow K={elbow_k}')
ax2.set_xlabel('Number of Clusters (K)')
ax2.set_ylabel('Silhouette Score')
ax2.set_title('Silhouette Score vs Number of Clusters')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Comparison of Optimal K values
algorithms = ['KMeans\n(Silhouette)', 'KMeans\n(Elbow)', 'Agglomerative', 'Spectral']
optimal_ks = [kmeans_best_k, elbow_k, agglo_best_k, spectral_best_k]
colors = ['skyblue', 'lightcoral', 'lightgreen', 'gold']

bars = ax3.bar(algorithms, optimal_ks, color=colors, alpha=0.7, edgecolor='black')
ax3.set_ylabel('Optimal Number of Clusters (K)')
ax3.set_title('Optimal K by Method')
ax3.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, k in zip(bars, optimal_ks):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'K={k}', ha='center', va='bottom', fontweight='bold')

# Plot 4: Silhouette Scores for Best K
best_silhouettes = [kmeans_best_score, agglo_best_score, spectral_best_score]
if dbscan_silhouette is not None:
    algorithms_sil = ['KMeans', 'Agglomerative', 'Spectral', 'DBSCAN']
    best_silhouettes.append(dbscan_silhouette)
    colors_sil = ['skyblue', 'lightgreen', 'gold', 'plum']
else:
    algorithms_sil = ['KMeans', 'Agglomerative', 'Spectral']
    colors_sil = ['skyblue', 'lightgreen', 'gold']

bars2 = ax4.bar(algorithms_sil, best_silhouettes, color=colors_sil, alpha=0.7, edgecolor='black')
ax4.set_ylabel('Silhouette Score')
ax4.set_title('Best Silhouette Scores by Algorithm')
ax4.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, score in zip(bars2, best_silhouettes):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.005,
             f'{score:.3f}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig("comprehensive_clustering_analysis.png", dpi=300, bbox_inches='tight')
plt.show()

# 9. Summary and Recommendations
print("\n" + "="*80)
print("CLUSTERING ANALYSIS SUMMARY")
print("="*80)
print(f"🔍 Elbow Method recommends: K = {elbow_k}")
print(f"📊 Best Silhouette Scores:")
print(f"   • KMeans (K={kmeans_best_k}): {kmeans_best_score:.3f}")
print(f"   • Agglomerative (K={agglo_best_k}): {agglo_best_score:.3f}")
print(f"   • Spectral (K={spectral_best_k}): {spectral_best_score:.3f}")
if dbscan_silhouette is not None:
    print(f"   • DBSCAN ({dbscan_n_clusters} clusters): {dbscan_silhouette:.3f}")

# Find the best overall method
best_method = max(results.items(), 
                 key=lambda x: x[1]['silhouette'] if x[1]['silhouette'] is not None else -1)

print(f"\n🏆 RECOMMENDED METHOD: {best_method[0]}")
if best_method[0] == 'KMeans':
    print(f"   Optimal K: {kmeans_best_k} (Silhouette) vs {elbow_k} (Elbow)")
    if kmeans_best_k == elbow_k:
        print("   ✅ Both methods agree on optimal K!")
    else:
        print("   ⚠️  Methods disagree - consider domain knowledge for final choice")
        
        
# Add this section after your existing code to display silhouette scores for K=2-10

print("\n" + "="*80)
print("SILHOUETTE SCORES FOR CLUSTERS 2-10")
print("="*80)

# Create a formatted table
print(f"{'K':<3} | {'KMeans':<8} | {'Agglomerative':<13} | {'Spectral':<8}")
print("-" * 45)

for i, k in enumerate(range(2, 11)):
    kmeans_score = f"{kmeans_scores[i]:.3f}" if kmeans_scores[i] != -1 else "N/A"
    agglo_score = f"{agglo_scores[i]:.3f}" if agglo_scores[i] != -1 else "N/A"
    spectral_score = f"{spectral_scores[i]:.3f}" if spectral_scores[i] != -1 else "N/A"
    
    print(f"{k:<3} | {kmeans_score:<8} | {agglo_score:<13} | {spectral_score:<8}")

# Also create a dictionary for easy access
silhouette_results = {
    'KMeans': dict(zip(range(2, 11), kmeans_scores)),
    'Agglomerative': dict(zip(range(2, 11), agglo_scores)),
    'Spectral': dict(zip(range(2, 11), spectral_scores))
}

print(f"\n📊 Silhouette scores are also available in the 'silhouette_results' dictionary")
print(f"   Example: silhouette_results['KMeans'][3] = {silhouette_results['KMeans'][3]:.3f}")