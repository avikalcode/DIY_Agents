```
cd diy_agents

--powershell------
Get-Content .env.dev | ForEach-Object { if ($_ -match '^\s*([^#=\s]+)\s*=\s*(.*)$') { [System.Environment]::SetEnvironmentVariable($Matches[1], $Matches[2].Trim("'").Trim('"'), "Process")}}

-- Bash---
export OPENAI_API_KEY="your-openai-key"
export PINECONE_API_KEY="your-pinecone-key"

echo $env:PINECONE_API_KEY

cd .\agents\rag_agents\

python agent_rag_chunks.py    
```
 # use case 
 **document 1** General return policy

 customers may return eligible products within 30 days of delivery

 **document 2** Electronics return policy

 eligible for return  within 7 days of delivery, subject to product inspection

  **document 3** Damaged return policy

 eligible for return  within 48 hours of delivery

 ## scenerios
Query : can I return the damaged headphone after 10 days

**Problem 1 vector store -> Wrong context set for LLM :Fetched wrong document data [Reason -> incorrect embedding model| no proper semantic relation]**

It can happen that right context may not get searched because its semantic search , so it gets the general return policy as set the wrong context to LLM
instead of 7 days, ut searched and fetched 30 days

**Problem 2 LLM -> right context but over infomation in context sent to LLM**

because right but over information like General policy and electronics policy both were fetched and LLM not able to interpret correctly gave wrong information based on General policy

**solution:**
`give right context` 

## Ingestion : Chuckning technique (to store chunks so that right context can be searched)
```
- fixed chunking with overlapping
- Structural chunking
- Sematic chunking
```

###- 1. Fixed size chunking - break the documents in chunks considering the embeeding dimension(1024) 200-300 chunks

-- Issue: `Context lost` due to breaking text into fixed size chunks

-- `Resolve` (minimim context loose) : Chunking + `OverLapping` (data reduntant)

    eg:

    Overlapping :  200 chuncks

    [1-1000] chunks converted to vector v1 

    [800-1800] chunks converted to vector v2

    General idea : 400-600 chunks and 10%-20% overlapping chunks

###- 2. Structural chunking (Document Aware Chunking) - splitting document based on Arrangement of document* 

-- `Resolve`  : Chunk based on Title > subheadings > paragraph > sections > tables

        or 'split by line using \n' , there are mant 3rd party library that help in splitting documents
        eg

        Title: Refund policy

        Sub Heading 1

        .....................

        ................................

        Sub Heading 2

        .....

        .........

        Create:

        chunk1  : Title + sub heading 1

        chunk 2 : sub heading 1

### 3. Semantic chunking  - required when unstructured unrelated consiqutive paragraph that cannot be pre-processed

`Resolve` : 

- Step 1- Chunking based on small lines (full-stop `'`) 'context is lost because of small chunks and top-k will further make the context loose'

    Line1 (chunks) -> v1 [x1,y1,z1...1024]

    Line2 (chunks) -> v2 [x2,y2,z2...1024]

- Step 2- To overcome issue in Step 1 

    -- v1, v2, v3...vn are in series 

    -- create cosine similarity of adjacent vectors [v1-v2] > [v2-v3] > [v3-v4]
    The lines which are related will have more similarity
    The lines which have low similarity will have less similarity score

    if v1-v2 -> 0.96

    and v2-v3 - 0.98

    but v3-v4 - 0.36

    it means v1 (line1), v2 (line2), v3 (line 3) are similar and hence create chunk  of line 1 + line 2 + line 3 i.e

    line 1 + line 2 + line 3 -> c1 --> v1

    line 4 + line 5          -> c2 --> v2

    `trade off` will take time to create index but better relationship and no too-small or too big-chunks


## Retrival technique

### top-k (top-k = 4)
Return top k context : K - 1...n

- use case

`how to decide 'k' decide on based on hit and try its better to keep based on CHUNKING tech, do unit test to print the data and then decide the size of k`

chunk 1 - 0.97

chunk 2 - 0.91

chunk 3 - 0.98

chunk 4 - 0.96

chunk 5 - 0.76

*k small - if we take top 3, then chunl 4 will be left out and that many have good information* 

*k big - if we take top 5, then irrelevent chunk also come in that have weal sematic relation with question* 

### similarity Threshold
*use case if the llm and document is for customer care and question asked is not related like  " who won the IPL in 2026*

- it retured chunks for top--k=3 [ c1-> .40   c2->0.30   c2-> 0.20 ]

 so it still gave the context to llm even though the question was irrelevent, and LLM responsed based on that

 that is why have creteria `THRESHOLD` for sematic search i.e threshold = 0.90, so no unrelated chunks will be retrieved

 ### Metadata filtering (filter expression) - category searching based on metadata

 `vector db --> store 'vector' + 'Metadata'`

- search for metadata (category) first 
- then after  go for chunk vectors search in those chunks that are returned by metada search

### keyword search 

*use case if the user ask for procuct1 which is same as product1 which have some specification difference only*

- go for keyword search (using `BM25 algorithm`) + semantic search = combined search send to LLM

- `RRF - Reciprocal Rank Fusion` to combine vector + text : **uses both search results and try to form 1 rank out of search results to arrange documents in order**

### ReRanking Models(query + documents) to get relevant document related to query in Order   -> followed by Embeddings models  
- where question + each individual documents are embedded together to know which documents are related with question, while doing query 
*use case returned 5 documents (chunk) but if we only need 3 document then may be 4th Rank document which has more relevent information may get missed out*

```
Query -> E(Q) = Embedding(query) -> [a,b,c]

Document1 -> v1 [x1,y1,z1]
Document2 -> v1 [x2,y2,z2]
....
..

The problem is all embeddings for Query(E) and Documents1 (E), Document2 (E) are not related when their embeddings are independent of each other while creation.   

ReRanking models -> [Query + doc] => [Cross Encoder Model] (no embeddings is done here) -> gets [relevance score] (how useful document is for particular query)
```

`how to do`
- STAGE 1
-- 1. Customer Query --> vector embeddings -> Q[a,b,c]
-- 2. Retrieve top 10-20 similar documents having 
- STAGE 2
-- `Re-Ranking` to get all document in oder (which document is more meaning ful comes first)
-- Get top 3 or 4 
-- send that to `LLM`

