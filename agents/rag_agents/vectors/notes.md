# vector database
```
- KNN
- ANN
```

`movies`

1. Instellar vector -> [e1,e2.....]

2. Batman vector    -> [e1,e2.....]

3. Batman vector   -> [e1,e2.....]

4. Superman vector  -> [e1,e2.....]

Query = "a space sci fi movie" - > [x,y.....]

`similarity score`

- Eucidian distance

- Cosine similarity

`get score of simlarity serach with queru and eack move vecore`

Query with Instellart  SCORE = 0.97

Query with Batman      SCORE = 0.62

Query with Titanic     SCORE = 0.28

Query with Superman    SCORE = 0.81

```
for vector v in vectorlist:
    x= similarity (Q,V)
    similarityScore(x)

sort(similarityScore)
return top-k
```
the sort of the scores , top 2 will het instellar, superman 

# Search 
## KNN algorithm (Brute Force/ slowest but exact match)--> to know NEAREST "movies" with are related to user "QUERY"

`N` = 100,000,000 vectors

`D` = 1536 is the **dimension of each vector**

`If Q vector is compared with every 'N' vetor ` = N * Q

cosine similarity   -> {Q[1]*v[1]) + (Q[1]*v[2]) + (Q[n] * V[n]}

                    -> (Q[i] * v[i]) * '1536 dimension`

                    -> 1536 * 100 million --> 15 billion

                    - get a list of 15 billion vectors, that need to be sorted (or use priority key, heap basically to get top elements)

## ANN (Approximate nearest neibhour) (faster than KNN but less accurate than in terms relative ordering that will miss top k )

`chhose less vector space`

```
1. IVF  : Inverted File Index
2. HNSW : Hirerarchical Navigable Small Worlds
```

Instead of searching relation score through scanning all vecors 100 million, we reduce the search to 1000 only, that is drastical improvenet in searching by decreasing `VECTOR SPACE`

we get group of vectors with are already related  

|

|                   |o     |

|                   |o    o|

|   |o o|

|   |o o|  o

|   o

|

--------------------------

Suppose top 10 sci-fi movies return 

Q(KNN) -> A, B, C, D, E, F, G, H, I , J  10 acurate resulys

Q(ANN) -> A, B, C, D, X, F, G, H, I , Y  8 acurate results 2 relatively 

`ReCall = correct outcomes/ total outcomes`

Recall@10 = 8/10 = 0.8 = > 80 %

### IVF algo : 

Breaking the vector space in cluster (group) eg 1000 movie cluster

1000000 (1 million vector) => break into 1000 clusrer = > 1000000 / 1000 vector per cluster = 1000 (cluster in vector space)

now Q (query cluster is compared with all cluster to know hich one closed cluster to Q) 

and then compare q vector with vectors present in that cluster which are nearest

`approach` how to know which cluster is closest

**centroid**

- k-meand algo is used to know the average of all vectors in each cluster [ c0, c1, ......c999]

- compare Q vector with all centroids and choose that cluster which is nearest to Q vector [ result0, result1, ...result999]

- return top k vectors 

**clustering/ indexing is done earlier**

increase number of cluster to compare to get 
- Recoil greater and acuuracy improvement
- latency increases

### HSNW 
STEP 1- store vector's **metadata** in `graph nodes` and connected through `edges` instead of breaking into cluster

Lets say vevtor A B C D .. have cordinates, now get lengrh of euciian distance of queruy vector from each graph 

distance (A,Q) --> 10

distance (B,Q) --> 8

distance (C,Q) --> 9

distance (d,Q) --> 9

comparing through A and its relation gets lowest distance 

STEP 2 - move through later

**create Nodes**