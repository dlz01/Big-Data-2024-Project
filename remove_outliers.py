import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
import heapq
from scipy.spatial.distance import euclidean

def MBR_endpoints(cluster):
  sigma = len(cluster[0])
  r_min = []
  r_max = []
  for i in range(sigma):
    max_coord = float('-inf')
    min_coord = float('inf')
    for point in cluster:
      min_coord = min(min_coord, point[i])
      max_coord = max(max_coord, point[i])
    r_min.append(min_coord)
    r_max.append(max_coord)
  return r_min, r_max

def MINDIST(R, S):
  r_min, r_max = MBR_endpoints(R)
  s_min, s_max = MBR_endpoints(S)
  sigma = len(r_min)
  x = 0
  for i in range(sigma):
    if s_max[i]<r_min[i]:
      xi = r_min[i]-s_max[i]
    elif r_max[i]<s_min[i]:
      xi =s_min[i]-r_max[i]
    else:
      xi = 0
    x += xi**2
  return x

def MAXDIST(R,S):
    r_min, r_max = MBR_endpoints(R)
    s_min, s_max = MBR_endpoints(S)
    sigma = len(r_min)
    x = 0
    for i in range(sigma):
      xi = max(abs(s_max[i]-r_min[i]), abs(r_max[i]-s_min[i]))
      x += xi**2
    return x

class Node:
    def __init__(self, data=None):
        self.data = data
        self.child = None
    def is_leaf(self, node):
        return node.child is None

class Tree:
    def __init__(self):
        self.root = None

    def insert(self, data):
        new_node = Node(data)
        if self.root is None:
            self.root = new_node
        else:
            self._insert_recursive(self.root, new_node)

    def _insert_recursive(self, current_node, new_node):
        if current_node.child is None:
            current_node.child = new_node
        else:
            self._insert_recursive(current_node.child, new_node)


class MaxHeap:
    def __init__(self):
        self.heap = []
    def push(self, arr, distance):
        heapq.heappush(self.heap, (distance*(-1), arr))
    def top(self):
        if self.heap:
            return self.heap[0][1]
    def top_points(self):
        if self.heap:
            return len(self.heap[0][1])
    def delete_top(self):
        if self.heap:
            return heapq.heappop(self.heap)[1]
    def top_distance(self):
      if self.heap:
          return (-1)*self.heap[0][0]
    def num_points(self):
        return sum(len(arr) for _, arr in self.heap)

class MinHeap:
    def __init__(self):
        self.heap = []
    def push(self, arr, distance):
        heapq.heappush(self.heap, (distance, arr))
    def top(self):
        if self.heap:
            return self.heap[0][1]
    def top_points(self):
        if self.heap:
            return len(self.heap[0][1])
    def delete_top(self):
        if self.heap:
            return heapq.heappop(self.heap)[1]
    def top_distance(self):
        if self.heap:
            return self.heap[0][0]
    def num_points(self):
        return sum(len(arr) for _, arr in self.heap)

class Partition:
    def __init__(self, points=None,upper=None, lower=None, neighbors=None):
        self.points = points
        self.upper = upper
        self.lower = lower
        self.neighbors = neighbors if neighbors is not None else []

# Step1: Generate Partitions
def generate_partitions(data,n_clusters):
  clustering = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
  clustering.fit(data)
  cluster_labels = clustering.labels_
  partitions = {}
  for i, label in enumerate(cluster_labels):
    if label not in partitions:
        partitions[label] = []
    partitions[label].append(data[i])
  combined_clusters = []
  for cluster in partitions.values():
    combined_clusters.append(cluster)
  return combined_clusters

# Step2: Bounds for D^k
def compute_lower_upper(Root, P, k, minDkDist):
  nodeList = [Root]
  P.lower = float('inf')
  P.upper = float('inf')
  lowerHeap = MaxHeap()
  upperHeap = MaxHeap()
  node = Root
  while node.is_leaf is False:
    nodeList.append(node.child)
    node = node.child
  while nodeList:
    node = nodeList[0]
    nodeList = nodeList[1:]
    if MINDIST(P.points, node.data) < P.lower:
      lowerHeap.push(node.data, MINDIST(P.points, node.data))
      while lowerHeap.num_points()-lowerHeap.top_points()>=k:
        lowerHeap.delete_top()
      if lowerHeap.num_points() >= k:
        P.lower = MINDIST(P.points, lowerHeap.top())
    if MAXDIST(P.points, node.data) < P.upper:
      upperHeap.push(node.data, MAXDIST(P.points, node.data))
      while upperHeap.num_points()-upperHeap.top_points() >= k:
            upperHeap.delete_top()
      if lowerHeap.num_points() >= k:
        P.upper = MAXDIST(P.points, upperHeap.top())
      if P.upper <= minDkDist:
        return
  return

# Step3: Candidate Partitions
def compute_candidate_partitions(PSet, k, n):
  tree = Tree()
  for P in PSet:
    tree.insert(P)
  partHeap = MinHeap()
  minDkDist = 0
  par_list = []
  for P in PSet:
    Par = Partition(points=P)
    par_list.append(Par)
    compute_lower_upper(tree.root, Par, k, minDkDist)
    if Par.lower > minDkDist:
            partHeap.push(P, Par.lower)
            while partHeap.num_points()-partHeap.top_points() >= n:
                partHeap.delete_top()
            if partHeap.num_points() >= n:
                minDkDist = partHeap.top_distance()

  candSet = []
  for P in par_list:
    if P.upper >= minDkDist:
      candSet.append(P)
      for Q in PSet:
        if MINDIST(P.points, Q) <= P.upper:
          P.neighbors.append(Q)
  return candSet

# Step4: Ourliers in Candidate Partitions
def getKthNeighborDist(neighbors,target_p,k,minDKDist):
    nearHeap = MaxHeap()
    DkDist = float('inf')
    for neighbor_par in neighbors:
      for neighbor_p in neighbor_par:
        if euclidean(target_p, neighbor_p)<DkDist:
          nearHeap.push(neighbor_p, euclidean(target_p, neighbor_p))
        if len(nearHeap.heap)>k:
            nearHeap.delete_top()
        if len(nearHeap.heap) == k:
            DkDist = nearHeap.top_distance()
        if DkDist<= minDKDist:
          return DkDist
    return DkDist

# Step4: Ourliers in Candidate Partitions
def compute_outlier_index(k,n,dataset):
  tree = Tree()
  for p in dataset:
    tree.insert(p)
  outHeap = MinHeap()
  minDkDist = 0
  for p in dataset:
    for target_p in p.points:
      DkDist = getKthNeighborDist(p.neighbors,target_p,k,minDkDist)
      if DkDist>minDkDist:
        outHeap.push(target_p, DkDist)
        if len(outHeap.heap)>n:
          outHeap.delete_top()
        if len(outHeap.heap)== n:
          minDkDist = outHeap.top_distance()
  return outHeap

# function
def remove_outliers(data, k, n,n_clusters):
  partitions = generate_partitions(data,n_clusters)
  print('partitions done')
  candSet = compute_candidate_partitions(partitions, k, n)
  print('candidate set done')
  outliers = compute_outlier_index(k,n,candSet)
  print('outliers done')
  outlier_list = []
  while outliers.heap:
    outlier_list.append(outliers.top())
    outliers.delete_top()
  for outlier in outlier_list:
    if outlier in data:
      data.remove(outlier)
  return data

if __name__ == "__main__":
   data = pd.read_excel('datasets/green_tripdata_2024-01.xlsx')
   cleaned_data = remove_outliers(data, 100, 200, 22)
   