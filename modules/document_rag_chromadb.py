"""
Document Management Tool with ChromaDB RAG Pipeline
Uses ChromaDB with sentence-transformers for embeddings (no API quota limits)
"""
import os
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class ChromaDBRAGTool:
    """
    Tool for LLM to manage documents with ChromaDB RAG pipeline
    Uses local sentence-transformers model - NO API costs or quotas!
    """
    
    def __init__(self, storage_path: str = "chromadb_storage", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize ChromaDB RAG Tool
        
        Args:
            storage_path: Path to store ChromaDB data
            model_name: Sentence transformer model (default: all-MiniLM-L6-v2 - 384 dims, fast)
        """
        self.storage_path = storage_path
        self.docs_path = os.path.join(storage_path, "documents")
        self.index_path = os.path.join(storage_path, "index.json")
        
        # Create directories
        os.makedirs(self.docs_path, exist_ok=True)
        
        print(f"Loading embedding model: {model_name}...")
        # Initialize sentence transformer (runs locally, no API needed!)
        self.embedding_model = SentenceTransformer(model_name)
        print(f"✓ Embedding model loaded: {model_name}")
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=storage_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="legal_documents",
            metadata={"description": "Legal documents for LuminaryAI"}
        )
        
        # Load or create index
        self.index = self._load_index()
        
        print(f"✓ ChromaDB initialized with {self.collection.count()} documents")
    
    def _load_index(self) -> Dict:
        """Load document index from file"""
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"documents": {}}
    
    def _save_index(self):
        """Save document index to file"""
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def _generate_doc_id(self, content: str) -> str:
        """Generate unique document ID"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk (reduced for better semantic coherence)
            overlap: Overlap between chunks
        """
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_id": chunk_index,
                        "text": current_chunk.strip(),
                        "length": len(current_chunk)
                    })
                    chunk_index += 1
                    # Add overlap
                    words = current_chunk.split()
                    overlap_text = " ".join(words[-overlap//5:]) if len(words) > overlap//5 else ""
                    current_chunk = overlap_text + "\n" + para + "\n\n"
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append({
                "chunk_id": chunk_index,
                "text": current_chunk.strip(),
                "length": len(current_chunk)
            })
        
        return chunks
    
    # ==================== TOOL METHODS ====================
    
    def add_document(
        self, 
        content: str, 
        title: str, 
        metadata: Optional[Dict] = None,
        doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new document to the RAG system
        
        Args:
            content: Document text content
            title: Document title
            metadata: Optional metadata
            doc_id: Optional document ID (if not provided, will be generated from content hash)
            
        Returns:
            Result dictionary with doc_id and status
        """
        if doc_id is None:
            doc_id = self._generate_doc_id(content)
        
        # Check if document already exists
        if doc_id in self.index["documents"]:
            return {
                "success": False,
                "doc_id": doc_id,
                "message": "Document already exists",
                "existing": True
            }
        
        # Save document content
        doc_file = os.path.join(self.docs_path, f"{doc_id}.txt")
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Chunk the document
        chunks = self._chunk_text(content)
        
        # Generate embeddings for all chunks (batch processing is faster)
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_model.encode(
            chunk_texts,
            show_progress_bar=False,
            convert_to_numpy=True
        ).tolist()
        
        # Add chunks to ChromaDB
        chunk_ids = []
        chunk_metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{chunk['chunk_id']}"
            chunk_ids.append(chunk_id)
            chunk_metadatas.append({
                "doc_id": doc_id,
                "title": title,
                "chunk_index": chunk["chunk_id"],
                "length": chunk["length"],
                **(metadata or {})
            })
        
        # Add to ChromaDB collection
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=chunk_metadatas
        )
        
        # Update index
        self.index["documents"][doc_id] = {
            "doc_id": doc_id,
            "title": title,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat(),
            "chunk_count": len(chunks),
            "char_count": len(content),
            "word_count": len(content.split())
        }
        
        self._save_index()
        
        return {
            "success": True,
            "doc_id": doc_id,
            "title": title,
            "chunks_created": len(chunks),
            "message": f"Document '{title}' added successfully"
        }
    
    def search_documents(
        self, 
        query: str, 
        top_k: int = 5,
        doc_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search documents using semantic similarity
        
        Args:
            query: Search query
            top_k: Number of top results to return
            doc_filter: Optional document ID to search within
            
        Returns:
            Search results with relevant chunks
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True
        ).tolist()[0]
        
        # Build filter if specified
        where_filter = None
        if doc_filter:
            where_filter = {"doc_id": doc_filter}
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "chunk_id": results['ids'][0][i],
                    "doc_id": results['metadatas'][0][i]['doc_id'],
                    "text": results['documents'][0][i],
                    "similarity": 1 - results['distances'][0][i],  # Convert distance to similarity
                    "doc_title": results['metadatas'][0][i]['title']
                })
        
        return {
            "success": True,
            "query": query,
            "results_count": len(formatted_results),
            "total_searched": self.collection.count(),
            "results": formatted_results
        }
    
    def query_document(
        self, 
        doc_id: str, 
        question: str
    ) -> Dict[str, Any]:
        """
        Ask a question about a specific document using RAG
        
        Args:
            doc_id: Document ID
            question: Question to ask
            
        Returns:
            Answer based on document content
        """
        if doc_id not in self.index["documents"]:
            return {
                "success": False,
                "message": f"Document {doc_id} not found"
            }
        
        # Search within this document
        search_results = self.search_documents(question, top_k=3, doc_filter=doc_id)
        
        if not search_results['results']:
            return {
                "success": False,
                "message": "No relevant content found in document"
            }
        
        # Build context from top chunks
        context = "\n\n".join([r['text'] for r in search_results['results']])
        
        # Generate answer using Gemini LLM (only for generation, not embeddings)
        try:
            import google.generativeai as genai
            from config import Config
            
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            model = genai.GenerativeModel(Config.LLM_MODEL)
            
            prompt = f"""Based on the following document excerpts, answer the question.

Document: {self.index['documents'][doc_id]['title']}

Context:
{context}

Question: {question}

Provide a clear, accurate answer based only on the context provided. If the answer cannot be found in the context, say so.

Answer:"""
            
            response = model.generate_content(prompt)
            answer = response.text
            
        except Exception as e:
            answer = f"Error generating answer: {str(e)}\n\nRelevant context found:\n{context[:500]}..."
        
        return {
            "success": True,
            "doc_id": doc_id,
            "doc_title": self.index['documents'][doc_id]['title'],
            "question": question,
            "answer": answer,
            "sources": search_results['results']
        }
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Retrieve full document"""
        if doc_id not in self.index["documents"]:
            return {
                "success": False,
                "message": f"Document {doc_id} not found"
            }
        
        doc_file = os.path.join(self.docs_path, f"{doc_id}.txt")
        if not os.path.exists(doc_file):
            return {
                "success": False,
                "message": "Document file not found"
            }
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        doc_info = self.index['documents'][doc_id]
        
        return {
            "success": True,
            "doc_id": doc_id,
            "title": doc_info['title'],
            "content": content,
            "metadata": doc_info['metadata'],
            "added_at": doc_info['added_at'],
            "stats": {
                "chunks": doc_info['chunk_count'],
                "characters": doc_info['char_count'],
                "words": doc_info['word_count'],
                "added_at": doc_info['added_at']
            }
        }
    
    def list_documents(self) -> Dict[str, Any]:
        """List all documents"""
        docs = []
        for doc_id, doc_info in self.index['documents'].items():
            docs.append({
                "doc_id": doc_id,
                "title": doc_info['title'],
                "chunks": doc_info['chunk_count'],
                "words": doc_info['word_count'],
                "added_at": doc_info['added_at'],
                "metadata": doc_info.get('metadata', {})
            })
        
        return {
            "success": True,
            "count": len(docs),
            "documents": docs
        }
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document"""
        if doc_id not in self.index["documents"]:
            return {
                "success": False,
                "message": f"Document {doc_id} not found"
            }
        
        # Get all chunk IDs for this document
        results = self.collection.get(where={"doc_id": doc_id})
        chunk_ids = results['ids']
        
        # Delete from ChromaDB
        if chunk_ids:
            self.collection.delete(ids=chunk_ids)
        
        # Delete document file
        doc_file = os.path.join(self.docs_path, f"{doc_id}.txt")
        if os.path.exists(doc_file):
            os.remove(doc_file)
        
        # Remove from index
        doc_title = self.index['documents'][doc_id]['title']
        del self.index['documents'][doc_id]
        self._save_index()
        
        return {
            "success": True,
            "doc_id": doc_id,
            "title": doc_title,
            "chunks_deleted": len(chunk_ids) if chunk_ids else 0,
            "message": f"Document '{doc_title}' deleted successfully"
        }
    
    def compare_documents(self, doc_id1: str, doc_id2: str) -> Dict[str, Any]:
        """
        Compare two documents and generate analysis
        
        Args:
            doc_id1: First document ID
            doc_id2: Second document ID
            
        Returns:
            Comparison analysis
        """
        # Get both documents
        doc1_result = self.get_document(doc_id1)
        doc2_result = self.get_document(doc_id2)
        
        if not doc1_result['success']:
            return {"success": False, "message": f"Document 1 not found: {doc_id1}"}
        if not doc2_result['success']:
            return {"success": False, "message": f"Document 2 not found: {doc_id2}"}
        
        # Generate comparison using Gemini LLM
        try:
            import google.generativeai as genai
            from config import Config
            
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            model = genai.GenerativeModel(Config.LLM_MODEL)
            
            prompt = f"""Compare these two legal documents and provide a detailed analysis:

Document 1: {doc1_result['title']}
{doc1_result['content'][:2000]}...

Document 2: {doc2_result['title']}
{doc2_result['content'][:2000]}...

Provide a detailed comparison with:
1. Key Similarities
2. Key Differences
3. Conflicting Provisions (if any)
4. Complementary Aspects
5. Overall Assessment

Comparison:"""
            
            response = model.generate_content(prompt)
            comparison = response.text
            
        except Exception as e:
            comparison = f"Error generating comparison: {str(e)}\n\nBasic comparison:\n"
            comparison += f"Document 1: {doc1_result['stats']['words']} words, {doc1_result['stats']['chunks']} chunks\n"
            comparison += f"Document 2: {doc2_result['stats']['words']} words, {doc2_result['stats']['chunks']} chunks"
        
        return {
            "success": True,
            "doc1": {
                "id": doc_id1,
                "title": doc1_result['title']
            },
            "doc2": {
                "id": doc_id2,
                "title": doc2_result['title']
            },
            "comparison": comparison
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG statistics"""
        total_docs = len(self.index['documents'])
        total_chunks = self.collection.count()
        total_words = sum(doc['word_count'] for doc in self.index['documents'].values())
        
        # Build document list
        documents = []
        for doc_id, doc_info in self.index['documents'].items():
            documents.append({
                "doc_id": doc_id,
                "title": doc_info['title'],
                "words": doc_info['word_count'],
                "chunks": doc_info['chunk_count']
            })
        
        return {
            "success": True,
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "total_words": total_words,
            "storage_path": self.storage_path,
            "documents": documents
        }
    
    def semantic_search_all(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """
        Semantic search across ALL documents
        Groups results by document
        """
        # Search all chunks
        results = self.search_documents(query, top_k=top_k * 2)  # Get more chunks
        
        if not results['results']:
            return {
                "success": True,
                "query": query,
                "documents": []
            }
        
        # Group by document
        doc_groups = {}
        for result in results['results']:
            doc_id = result['doc_id']
            if doc_id not in doc_groups:
                doc_groups[doc_id] = {
                    "doc_id": doc_id,
                    "title": result['doc_title'],
                    "max_similarity": result['similarity'],
                    "chunk_count": 1,
                    "top_chunks": [result]
                }
            else:
                doc_groups[doc_id]['chunk_count'] += 1
                doc_groups[doc_id]['top_chunks'].append(result)
                if result['similarity'] > doc_groups[doc_id]['max_similarity']:
                    doc_groups[doc_id]['max_similarity'] = result['similarity']
        
        # Sort by max similarity
        documents = sorted(doc_groups.values(), key=lambda x: x['max_similarity'], reverse=True)[:top_k]
        
        return {
            "success": True,
            "query": query,
            "documents": documents,
            "total_docs_found": len(documents)
        }
