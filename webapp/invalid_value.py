import pandas as pd
from sklearn.cluster import KMeans, DBSCAN

def invalid_value(df, columns):
    df = df.copy()
    for col in columns:
        df = remove_outliers(df, col)
    return df

def remove_outliers(df, col):
    if not pd.api.types.is_numeric_dtype(df[col]):
        return df
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    if IQR == 0:
        return df
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    filtered_df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    
    return filtered_df

# def remove_outliers_with_clustering(df, cols):
#     cols_numeric = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    
#     df_numeric = df[cols_numeric]
    
#     # Perform K-means clustering
#     kmeans = KMeans(n_clusters=2, random_state=0)  # with 2 clusters
#     kmeans.fit(df_numeric)
    
#     # Find the largest cluster
#     labels = pd.Series(kmeans.labels_)
#     largest_cluster = labels.mode()[0]
    
#     in_cluster = labels == largest_cluster
    
#     filtered_df = df[in_cluster]
    
#     return filtered_df

# def invalid_value(df, cols, eps=0.5, min_samples=5):
#     for col in cols:
#         df[col] = pd.to_numeric(df[col], errors='coerce')
#         df = df.dropna(subset=[col])
#     cols_numeric = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
#     if len(cols_numeric) == 0:
#         return df
#     # Extract the relevant columns
#     data = df[cols_numeric]
    
#     # Applying DBSCAN
#     dbscan = DBSCAN(eps=eps, min_samples=min_samples)
#     clusters = dbscan.fit_predict(data)
    
#     # Points classified as '-1' are the outliers
#     mask = clusters != -1
    
#     # Filter the dataframe to remove outliers
#     filtered_df = df[mask]

#     return filtered_df