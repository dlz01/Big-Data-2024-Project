import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster, cophenet
from scipy.spatial.distance import squareform
from edit_distance import edit_distance


def hierarchical_clustering(words, dist, threshold = 2):
    n = len(words)
    distance_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            distance = dist(words[i], words[j])
            distance_matrix[i, j] = distance
            distance_matrix[j, i] = distance

    # hierarchical clustering
    linked = linkage(squareform(distance_matrix), "single")

    clusters = fcluster(linked, threshold, criterion="distance")

    cluster_dict = {}
    for i, word in enumerate(words):
        cluster_label = clusters[i]
        if cluster_label not in cluster_dict:
            cluster_dict[cluster_label] = []
        cluster_dict[cluster_label].append(word)

    return cluster_dict


if __name__ == "__main__":
    words = ["hello", "thankk", "you", "thank", "lou", "thenk", "very", "much"]
    cluster_dict = hierarchical_clustering(words=words, dist=edit_distance)
    cluster_dict = hierarchical_clustering(words=[1, 5, 2, 3, 9, 100], dist=lambda x, y: abs(x - y), threshold = 2)
    print(cluster_dict)
    # for label, cluster in cluster_dict.items():
    #     print(f"Cluster {label}: {', '.join(cluster)}")
