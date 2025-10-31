# Document RAG Tool for LLM

## Overview

A comprehensive **Retrieval-Augmented Generation (RAG)** tool that allows LLMs to manage, access, and intelligently query documents using semantic search with Gemini embeddings.

## Features

### 🚀 Core Capabilities

- ✅ **Document Management** - Add, list, retrieve, delete documents
- ✅ **Semantic Search** - Vector-based similarity search using Gemini embeddings
- ✅ **Intelligent Chunking** - Paragraph-based chunking with configurable overlap
- ✅ **Q&A System** - Ask questions about specific documents
- ✅ **Multi-Doc Search** - Search across all documents with grouped results
- ✅ **Document Comparison** - Compare two documents using LLM
- ✅ **Persistent Storage** - JSON-based indexing with file storage
- ✅ **Metadata Support** - Attach custom metadata to documents

### 🔍 RAG Pipeline

```
1. Document → 2. Chunking → 3. Embedding Generation →
4. Storage → 5. Query Embedding → 6. Similarity Search →
7. Context Retrieval → 8. LLM Answer Generation
```

## Architecture

### Storage Structure

```
document_storage/
├── index.json              # Master index
├── documents/              # Full document files
│   ├── abc123.txt
│   └── def456.txt
└── chunks/                 # Document chunks with embeddings
    ├── abc123_0.json
    ├── abc123_1.json
    └── def456_0.json
```

### Index Format

```json
{
  "documents": {
    "abc123": {
      "doc_id": "abc123",
      "title": "Rental Agreement",
      "metadata": { "type": "rental" },
      "added_at": "2025-10-30T10:30:00",
      "chunk_count": 3,
      "char_count": 1500,
      "word_count": 250
    }
  },
  "chunks": {
    "abc123_0": {
      "doc_id": "abc123",
      "chunk_file": "abc123_0.json"
    }
  }
}
```

### Chunk Format

```json
{
  "chunk_id": "abc123_0",
  "doc_id": "abc123",
  "text": "chunk content...",
  "embedding": [0.123, -0.456, ...],
  "length": 500
}
```

## Usage

### 1. Initialize Tool

```python
from modules.document_rag_tool import DocumentRAGTool

tool = DocumentRAGTool(storage_path="document_storage")
```

### 2. Add Documents

```python
content = """
RENTAL AGREEMENT
This agreement is made on...
"""

result = tool.add_document(
    content=content,
    title="Mumbai Rental Agreement 2025",
    metadata={
        "type": "rental",
        "location": "Mumbai",
        "date": "2025-01-15"
    }
)

print(result)
# {
#   "success": True,
#   "doc_id": "abc123",
#   "chunks_created": 3,
#   "message": "Document added successfully"
# }
```

### 3. Search Documents (RAG)

```python
result = tool.search_documents(
    query="notice period requirements",
    top_k=5
)

for r in result["results"]:
    print(f"Document: {r['doc_title']}")
    print(f"Similarity: {r['similarity']:.4f}")
    print(f"Text: {r['text'][:200]}...\n")
```

### 4. Ask Questions

```python
result = tool.query_document(
    doc_id="abc123",
    question="What is the monthly rent amount?"
)

print(result["answer"])
# The monthly rent is Rs. 25,000 per month...

print(result["sources"])
# Shows which chunks were used to answer
```

### 5. Semantic Search All

```python
result = tool.semantic_search_all(
    query="termination and notice clauses",
    top_k=10
)

for doc in result["documents"]:
    print(f"{doc['title']} - Relevance: {doc['max_similarity']:.4f}")
```

### 6. Compare Documents

```python
result = tool.compare_documents(
    doc_id1="abc123",
    doc_id2="def456"
)

print(result["comparison"])
```

### 7. List & Manage

```python
# List all documents
result = tool.list_documents()
for doc in result["documents"]:
    print(f"{doc['title']} - {doc['words']} words")

# Get full document
result = tool.get_document("abc123")
print(result["content"])

# Delete document
result = tool.delete_document("abc123")
```

### 8. Get Statistics

```python
result = tool.get_statistics()
print(f"Total documents: {result['total_documents']}")
print(f"Total chunks: {result['total_chunks']}")
print(f"Total words: {result['total_words']}")
```

## API Endpoints

### Add Document

```http
POST /api/rag/documents
Authorization: Bearer <token>

{
  "content": "document text content",
  "title": "Document Title",
  "metadata": {"type": "contract", "date": "2025-01-15"}
}
```

### List Documents

```http
GET /api/rag/documents
Authorization: Bearer <token>
```

### Get Document

```http
GET /api/rag/documents/{doc_id}
Authorization: Bearer <token>
```

### Search Documents

```http
POST /api/rag/search
Authorization: Bearer <token>

{
  "query": "search query",
  "top_k": 5,
  "doc_filter": "optional_doc_id"
}
```

### Query Document

```http
POST /api/rag/documents/{doc_id}/query
Authorization: Bearer <token>

{
  "question": "What is the notice period?"
}
```

### Semantic Search All

```http
POST /api/rag/search/semantic
Authorization: Bearer <token>

{
  "query": "termination clauses",
  "top_k": 10
}
```

### Compare Documents

```http
POST /api/rag/documents/compare
Authorization: Bearer <token>

{
  "doc_id1": "abc123",
  "doc_id2": "def456"
}
```

### Delete Document

```http
DELETE /api/rag/documents/{doc_id}
Authorization: Bearer <token>
```

### Get Statistics

```http
GET /api/rag/statistics
Authorization: Bearer <token>
```

## Integration with Flask App

Add to your `app.py`:

```python
from modules.document_rag_routes import rag_bp

# Register blueprint
app.register_blueprint(rag_bp)
```

## Technical Details

### Embeddings

- **Model**: `models/embedding-001` (Gemini)
- **Dimension**: 768
- **Task Type**: `retrieval_document` for documents, `retrieval_query` for queries

### Chunking Strategy

- **Default Size**: 1000 characters
- **Overlap**: 200 characters
- **Method**: Paragraph-based with intelligent boundary detection
- **Preserves**: Sentence and paragraph context

### Similarity Calculation

- **Method**: Cosine similarity
- **Formula**: `dot(v1, v2) / (||v1|| * ||v2||)`
- **Range**: -1 to 1 (higher = more similar)

### Performance

- **Typical Chunk Time**: 50-100ms per document
- **Embedding Time**: ~200ms per chunk
- **Search Time**: ~100ms for 100 chunks
- **Storage**: ~2KB per chunk (including embedding)

## Use Cases

### 1. Legal Document Library

```python
# Add legal documents
tool.add_document(contract_text, "Service Agreement", {"type": "contract"})
tool.add_document(nda_text, "NDA Template", {"type": "nda"})

# Search across all
results = tool.semantic_search_all("confidentiality clauses")
```

### 2. Contract Analysis

```python
# Upload contract
result = tool.add_document(contract, "Client Contract 2025")
doc_id = result["doc_id"]

# Ask questions
answer1 = tool.query_document(doc_id, "What is the payment term?")
answer2 = tool.query_document(doc_id, "What are termination conditions?")
```

### 3. Document Comparison

```python
# Compare two versions
comparison = tool.compare_documents(
    "old_contract_id",
    "new_contract_id"
)
```

### 4. Knowledge Base

```python
# Build knowledge base
for doc_file in legal_docs:
    with open(doc_file) as f:
        content = f.read()
    tool.add_document(content, doc_file.stem, {"category": "legal"})

# Query knowledge base
results = tool.semantic_search_all("property transfer laws")
```

## Testing

Run the comprehensive test suite:

```bash
python test_document_rag_tool.py
```

Tests cover:

- ✓ Document addition with metadata
- ✓ Document listing
- ✓ Semantic search
- ✓ Document Q&A
- ✓ Cross-document search
- ✓ Document comparison
- ✓ Statistics retrieval
- ✓ Full document retrieval

## Advantages

### vs Traditional Vector Databases

| Feature          | Document RAG Tool | Vector DB            |
| ---------------- | ----------------- | -------------------- |
| Setup Complexity | Low               | High                 |
| Dependencies     | Gemini only       | Multiple libraries   |
| Storage          | File-based        | Database             |
| Portability      | High              | Medium               |
| Cost             | API only          | Infrastructure + API |
| Good For         | <100k docs        | 100k+ docs           |

### Key Benefits

✅ **Simple Setup** - No complex infrastructure  
✅ **Pure Python** - No external services  
✅ **Portable** - Easy to move/backup  
✅ **Transparent** - Human-readable storage  
✅ **Flexible** - Easy to customize  
✅ **Cost-Effective** - Pay per API call only

## Configuration

Required in `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-pro
```

Optional customization:

```python
tool = DocumentRAGTool(
    storage_path="custom_path"
)

# Custom chunking
tool._chunk_text(
    text,
    chunk_size=1500,  # Larger chunks
    overlap=300       # More overlap
)
```

## Error Handling

All methods return consistent response format:

### Success Response

```json
{
  "success": true,
  "data": {...}
}
```

### Error Response

```json
{
  "success": false,
  "message": "Error description"
}
```

## Limitations

- **Scale**: Best for <100,000 documents
- **Speed**: Linear search (O(n) for all chunks)
- **Memory**: Loads embeddings from disk
- **Concurrency**: No built-in locking

For larger scale, consider:

- Vector databases (Pinecone, Weaviate, Qdrant)
- Approximate nearest neighbors (ANN)
- Distributed storage

## Future Enhancements

Potential improvements:

- [ ] Batch embedding generation
- [ ] Async search operations
- [ ] Compression for embeddings
- [ ] Caching layer
- [ ] Multi-language support
- [ ] Document versioning
- [ ] Access control per document
- [ ] Export/import functionality

## Conclusion

The Document RAG Tool provides a lightweight, production-ready solution for document management with intelligent search capabilities, perfect for legal AI applications with moderate document volumes.
