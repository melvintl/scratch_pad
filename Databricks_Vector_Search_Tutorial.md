# Databricks Vector Search — From Zero to Querying

**A hands-on tutorial | 5 exercises | ~15 minutes total**

---

## What You'll Build

By the end of this tutorial, you'll have:

1. A **Vector Search endpoint** (the compute that powers search)
2. A **Delta table** with sample text data
3. A **Vector Search index with managed embeddings** (Databricks computes embeddings for you)
4. A **Vector Search index with pre-computed embeddings** (you compute them yourself)
5. Experience **querying both indexes** from Python and SQL

**Prerequisites:** A Databricks workspace with Unity Catalog enabled and serverless compute available. You should have a catalog and schema you can write to (the examples use `my_catalog.my_schema` — replace with yours throughout).

---

---

## Exercise 1 — Create a Vector Search Endpoint

`⏱ 2 min`

### Concept

A Vector Search **endpoint** is the compute resource that hosts your indexes and handles queries. Think of it like a SQL warehouse, but for vector similarity search. You create one endpoint and then attach multiple indexes to it. Endpoints auto-scale and are serverless — you don't manage any infrastructure.

> **Important:** An endpoint is not an index. The endpoint is the compute; the index is the data. You'll create the endpoint first, then create indexes on it.

### Hands-On

Create a new Python notebook and run this in your first cell:

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Create a vector search endpoint
# This takes 5-10 minutes to provision, so we kick it off and move on
endpoint = w.vector_search_endpoints.create_endpoint(
    name="my-vector-endpoint",
    endpoint_type="STANDARD"
)

print(f"Endpoint creation started: {endpoint.name}")
print("Status: provisioning (this takes ~5-10 min, we'll continue while it provisions)")
```

While the endpoint provisions, check it in the UI:

1. Go to **Catalog** → click the **gear icon** or search for "Vector Search" in the sidebar
2. Or go to **Compute** → look for a **"Vector Search"** tab
3. You should see `my-vector-endpoint` with a "Provisioning" status

> **Tip:** You only need one endpoint for many indexes. In a real workspace, you might already have one — check before creating a new one.

To check when it's ready:

```python
# Poll for endpoint readiness (run this cell periodically)
ep = w.vector_search_endpoints.get_endpoint(endpoint_name="my-vector-endpoint")
print(f"Status: {ep.endpoint_status.state}")
# You want to see: ONLINE
```

> **What You Learned:** A Vector Search endpoint is a shared compute resource you create once. It hosts your indexes and handles queries. It's serverless and auto-scales.

---

## Exercise 2 — Create a Source Delta Table

`⏱ 2 min`

### Concept

Vector Search indexes are built **on top of Delta tables**. The Delta table holds your source data (text, metadata, IDs), and the Vector Search index makes it searchable by semantic similarity. For this to work with auto-sync, the table needs **Change Data Feed** enabled — this lets Vector Search detect inserts, updates, and deletes automatically.

### Hands-On

Run this SQL in a notebook cell (switch the cell to SQL, or use `spark.sql()`):

```sql
-- Replace my_catalog.my_schema with your own catalog and schema
CREATE OR REPLACE TABLE my_catalog.my_schema.product_docs (
    doc_id BIGINT NOT NULL,
    title STRING NOT NULL,
    content STRING NOT NULL,
    category STRING
)
TBLPROPERTIES (delta.enableChangeDataFeed = true);

INSERT INTO my_catalog.my_schema.product_docs VALUES
  (1, 'Getting Started with Databricks',
   'Databricks is a unified analytics platform that combines data engineering, data science, and machine learning. It runs on top of cloud providers like AWS, Azure, and GCP.',
   'overview'),

  (2, 'What is Unity Catalog',
   'Unity Catalog is the unified governance solution for all data and AI assets on the Databricks platform. It provides centralized access control, auditing, lineage, and data discovery.',
   'governance'),

  (3, 'Introduction to Delta Lake',
   'Delta Lake is an open-source storage layer that brings ACID transactions to Apache Spark. It provides schema enforcement, time travel, and scalable metadata handling.',
   'storage'),

  (4, 'Model Serving Overview',
   'Databricks Model Serving provides a unified interface to deploy machine learning models and LLMs as REST API endpoints. It supports autoscaling, A/B testing, and OpenAI-compatible APIs.',
   'ai'),

  (5, 'What are Vector Embeddings',
   'Vector embeddings are numerical representations of data in a high-dimensional space. Similar items end up close together in this space, enabling semantic search and recommendation systems.',
   'ai'),

  (6, 'Building Data Pipelines',
   'Databricks supports both batch and streaming data pipelines using Apache Spark and Delta Live Tables. Pipelines can be orchestrated with Databricks Workflows.',
   'engineering'),

  (7, 'SQL Warehouses Explained',
   'SQL Warehouses provide serverless compute for running SQL queries against your lakehouse data. They auto-scale based on workload and support BI tool connections.',
   'compute'),

  (8, 'RAG Applications on Databricks',
   'Retrieval Augmented Generation combines vector search with LLMs. Documents are chunked, embedded, and indexed. At query time, relevant chunks are retrieved and passed to the LLM for grounded responses.',
   'ai');
```

Verify the data:

```sql
SELECT doc_id, title, category FROM my_catalog.my_schema.product_docs ORDER BY doc_id;
```

You should see 8 rows of product documentation across categories like overview, governance, storage, ai, engineering, and compute.

> **What You Learned:** Vector Search indexes are built on Delta tables. Enable Change Data Feed (`delta.enableChangeDataFeed = true`) so the index can auto-detect changes to your source data.

---

## Exercise 3 — Create an Index with Managed Embeddings

`⏱ 3 min (+ wait time for sync)`

### Concept

With **managed embeddings**, you point Vector Search at a text column and an embedding model, and Databricks does the rest — it reads your text, computes embeddings using the model you specify, stores them, and keeps them in sync as data changes. This is the simplest path: you don't need to know anything about embedding dimensions or vector formats.

The key ingredients are:
- **`embedding_source_column`** — which text column to embed (e.g., `content`)
- **`embedding_model_endpoint_name`** — which model computes the embeddings (e.g., `databricks-gte-large-en`)
- **`pipeline_type`** — `"TRIGGERED"` (you manually sync) or `"CONTINUOUS"` (auto-syncs on changes)

### Hands-On

First, make sure your endpoint from Exercise 1 is online:

```python
ep = w.vector_search_endpoints.get_endpoint(endpoint_name="my-vector-endpoint")
print(f"Endpoint status: {ep.endpoint_status.state}")
# Needs to be ONLINE before continuing
```

Now create the index:

```python
from databricks.vector_search.client import VectorSearchClient

vsc = VectorSearchClient()

# Create a managed embedding index
# Databricks will embed the 'content' column for you
index = vsc.create_delta_sync_index(
    endpoint_name="my-vector-endpoint",
    index_name="my_catalog.my_schema.product_docs_index",
    source_table_name="my_catalog.my_schema.product_docs",
    pipeline_type="TRIGGERED",
    primary_key="doc_id",
    embedding_source_column="content",
    embedding_model_endpoint_name="databricks-gte-large-en"
)

print(f"Index creation started: {index.name}")
```

> **Note:** `databricks-gte-large-en` is a Databricks-hosted embedding model (1024 dimensions, 8192 token window). It's available as a pay-per-token Foundation Model endpoint. If it's not available in your workspace, check the Serving page for alternative embedding endpoints like `databricks-bge-large-en`.

Trigger the initial sync and wait:

```python
import time

# Check index status
while True:
    idx = vsc.get_index(index_name="my_catalog.my_schema.product_docs_index")
    status = idx.describe()
    state = status.get("status", {}).get("ready", False)
    print(f"Index ready: {state}")
    if state:
        break
    time.sleep(30)

print("Index is ready for queries!")
```

> **Tip:** The initial sync takes a few minutes as it embeds all 8 documents. For larger tables (millions of rows), this can take longer. `CONTINUOUS` pipeline mode would keep it auto-updated, but `TRIGGERED` gives you more control.

> **What You Learned:** Managed embeddings are the easiest path — tell Databricks which column to embed and which model to use, and it handles everything. You never see or manage the actual vectors.

---

## Exercise 4 — Create an Index with Pre-Computed Embeddings

`⏱ 3 min (+ wait time for sync)`

### Concept

Sometimes you want to **compute embeddings yourself** — maybe you're using a custom model, or you want to embed multiple columns, or you need more control over the process. With pre-computed embeddings, you generate the vectors, store them in a Delta table column as `ARRAY<FLOAT>`, and then point Vector Search at that column.

This approach gives you full control but requires you to keep embeddings in sync when source data changes.

### Hands-On

**Step 1: Generate embeddings using the foundation model API**

```python
from openai import OpenAI

# Get the OpenAI-compatible client
client = w.serving_endpoints.get_open_ai_client()

# Load our source data
docs_df = spark.table("my_catalog.my_schema.product_docs").toPandas()

# Generate embeddings for each document's content
embeddings = []
for _, row in docs_df.iterrows():
    response = client.embeddings.create(
        model="databricks-gte-large-en",
        input=row["content"]
    )
    embeddings.append(response.data[0].embedding)

docs_df["content_embedding"] = embeddings

print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding dimension: {len(embeddings[0])}")
# Should print: Embedding dimension: 1024
```

**Step 2: Save embeddings to a new Delta table**

```python
from pyspark.sql.types import StructType, StructField, LongType, StringType, ArrayType, FloatType

# Convert back to Spark DataFrame
schema = StructType([
    StructField("doc_id", LongType(), False),
    StructField("title", StringType(), False),
    StructField("content", StringType(), False),
    StructField("category", StringType(), True),
    StructField("content_embedding", ArrayType(FloatType()), False)
])

spark_df = spark.createDataFrame(docs_df[["doc_id", "title", "content", "category", "content_embedding"]].values.tolist(), schema)

spark_df.write.mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable("my_catalog.my_schema.product_docs_with_embeddings")

# Enable change data feed
spark.sql("""
    ALTER TABLE my_catalog.my_schema.product_docs_with_embeddings
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

print("Embeddings table created!")
```

Verify what the embeddings look like:

```python
display(spark.sql("""
    SELECT doc_id, title,
           size(content_embedding) as embedding_dims,
           slice(content_embedding, 1, 5) as first_5_values
    FROM my_catalog.my_schema.product_docs_with_embeddings
"""))
```

**Step 3: Create the index pointing at the embedding column**

```python
# Create index with pre-computed embeddings
index_precomputed = vsc.create_delta_sync_index(
    endpoint_name="my-vector-endpoint",
    index_name="my_catalog.my_schema.product_docs_precomputed_index",
    source_table_name="my_catalog.my_schema.product_docs_with_embeddings",
    pipeline_type="TRIGGERED",
    primary_key="doc_id",
    embedding_vector_column="content_embedding",
    # No embedding_model_endpoint_name needed — we already computed them
)

print("Pre-computed embedding index creation started!")
```

Wait for it to be ready (same polling pattern as Exercise 3).

> **What You Learned:** Pre-computed embeddings give you full control — you generate the vectors yourself and store them as `ARRAY<FLOAT>` in Delta. The index just indexes the vectors you provide. Use this when you need custom embedding logic or models.

---

## Exercise 5 — Query Your Indexes

`⏱ 3 min`

### Concept

Now the fun part. You can query Vector Search indexes two ways: via the **Python SDK** (great for applications and notebooks) or via the **SQL `vector_search()` function** (great for analytics and SQL workflows). For managed embedding indexes, you pass a text query and Databricks embeds it for you. For pre-computed indexes, you can pass either text (if the index knows the model) or a raw vector.

### Hands-On

**Step 1: Simple similarity search (Python — managed embeddings)**

```python
# Get the managed embedding index
index = vsc.get_index(index_name="my_catalog.my_schema.product_docs_index")

# Search: "How do I govern my data?"
results = index.similarity_search(
    query_text="How do I govern my data?",
    columns=["doc_id", "title", "content", "category"],
    num_results=3
)

# Display results
for row in results["result"]["data_array"]:
    doc_id, title, content, category, score = row
    print(f"\n[Score: {score:.4f}] {title}")
    print(f"  Category: {category}")
    print(f"  Content: {content[:100]}...")
```

You should see the Unity Catalog doc ranked highest — it's the most semantically relevant to "govern my data" even though it doesn't contain the exact phrase.

**Step 2: Try different queries and observe the ranking**

```python
queries = [
    "How do I build a real-time streaming pipeline?",
    "What is RAG and how does it work?",
    "How do I deploy a machine learning model?",
]

for q in queries:
    results = index.similarity_search(
        query_text=q,
        columns=["title", "category"],
        num_results=2
    )
    print(f"\nQuery: {q}")
    for row in results["result"]["data_array"]:
        title, category, score = row
        print(f"  [{score:.4f}] {title} ({category})")
```

Notice how the search understands **meaning**, not just keywords. "How do I deploy a machine learning model?" should match the Model Serving doc, even though the query uses different words.

**Step 3: Search with filters**

```python
# Only search within the 'ai' category
results = index.similarity_search(
    query_text="How does search work?",
    columns=["title", "content"],
    filters={"category": "ai"},
    num_results=3
)

print("Results filtered to 'ai' category only:")
for row in results["result"]["data_array"]:
    title, content, score = row
    print(f"  [{score:.4f}] {title}")
```

Filtering is powerful for scoping searches — e.g., restrict to a department, document type, date range, or access level.

**Step 4: Query from SQL**

Switch to a SQL cell or use `spark.sql()`:

```sql
-- Semantic search from SQL (requires DBR 15.3+)
SELECT * FROM vector_search(
    index => 'my_catalog.my_schema.product_docs_index',
    query_text => 'How do I store data reliably?',
    num_results => 3
)
```

You should see the Delta Lake doc ranked highly — it's about reliable data storage with ACID transactions.

**Step 5: Query the pre-computed index with a raw vector**

```python
# First, embed your query manually
query_response = client.embeddings.create(
    model="databricks-gte-large-en",
    input="How do I govern my data?"
)
query_vector = query_response.data[0].embedding

# Now search the pre-computed index with the raw vector
index_precomputed = vsc.get_index(
    index_name="my_catalog.my_schema.product_docs_precomputed_index"
)

results = index_precomputed.similarity_search(
    query_vector=query_vector,
    columns=["title", "category"],
    num_results=3
)

print("Pre-computed index results:")
for row in results["result"]["data_array"]:
    title, category, score = row
    print(f"  [{score:.4f}] {title} ({category})")
```

The results should be identical to Step 1 — same query, same embeddings model, same data. The difference is just who computed the query embedding (you vs Databricks).

> **What You Learned:** Vector Search finds documents by **meaning**, not keywords. You can query with text (managed embeddings) or raw vectors (pre-computed). Filters let you scope searches. And the SQL `vector_search()` function brings semantic search into your SQL workflows.

---

---

## Quick Reference Card

### Key Objects

| Object | What It Is | How Many You Need |
|--------|-----------|-------------------|
| **Endpoint** | Compute that hosts indexes and handles queries | 1 per workspace (can host many indexes) |
| **Delta Table** | Your source data (text + metadata) | 1 per dataset |
| **Index** | The searchable vector index built on a Delta table | 1 per table you want to search |

### Managed vs Pre-Computed Embeddings

| | Managed | Pre-Computed |
|-|---------|-------------|
| **You provide** | Text column + model name | `ARRAY<FLOAT>` embedding column |
| **Databricks computes** | Embeddings automatically | Nothing — uses your vectors |
| **Best for** | Simplicity, standard models | Custom models, multi-column embedding, full control |
| **Query with** | `query_text="..."` | `query_vector=[...]` |

### Common Embedding Models

| Model | Dimensions | Max Tokens | Use Case |
|-------|-----------|------------|----------|
| `databricks-gte-large-en` | 1024 | 8,192 | General purpose (recommended) |
| `databricks-bge-large-en` | 1024 | 512 | Short text, high accuracy |

### Pipeline Types

| Type | Behaviour |
|------|-----------|
| `TRIGGERED` | You manually call `index.sync()` to update |
| `CONTINUOUS` | Auto-syncs as source Delta table changes |

---

## Cleanup (Optional)

If you want to remove everything you created:

```python
# Delete indexes
vsc.delete_index(index_name="my_catalog.my_schema.product_docs_index")
vsc.delete_index(index_name="my_catalog.my_schema.product_docs_precomputed_index")

# Delete endpoint (only if you created it just for this tutorial)
w.vector_search_endpoints.delete_endpoint(endpoint_name="my-vector-endpoint")

# Drop tables
spark.sql("DROP TABLE IF EXISTS my_catalog.my_schema.product_docs")
spark.sql("DROP TABLE IF EXISTS my_catalog.my_schema.product_docs_with_embeddings")
```

---

## What's Next

Now that you can create and query vector indexes, the natural next step is **RAG** — combining Vector Search with an LLM to build a question-answering system that's grounded in your data. That's where vector search stops being a standalone feature and becomes the retrieval layer in an AI application.
