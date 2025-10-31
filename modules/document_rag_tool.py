"""
Document Management Tool with RAG Pipeline for LLM
Allows LLM to manage, access, and query documents using RAG
"""
import os
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai
from config import Config

class DocumentRAGTool:
    """
    Tool for LLM to manage documents with RAG pipeline
    Provides document indexing, retrieval, and intelligent querying
    """
    
    def __init__(self, storage_path: str = "document_storage"):
        """
        Initialize Document RAG Tool
        
        Args:
            storage_path: Path to store document data and embeddings
        """
        self.storage_path = storage_path
        self.docs_path = os.path.join(storage_path, "documents")
        self.index_path = os.path.join(storage_path, "index.json")
        self.chunks_path = os.path.join(storage_path, "chunks")
        
        # Create directories
        os.makedirs(self.docs_path, exist_ok=True)
        os.makedirs(self.chunks_path, exist_ok=True)
        
        # Initialize Gemini
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(Config.LLM_MODEL)
        self.embedding_model = 'models/embedding-001'
        
        # Load or create index
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """Load document index from file"""
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"documents": {}, "chunks": {}}
    
    def _save_index(self):
        """Save document index to file"""
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def _generate_doc_id(self, content: str) -> str:
        """Generate unique document ID"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """
        Split text into overlapping chunks with metadata
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries
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
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Gemini"""
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Embedding error: {str(e)}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    # ==================== TOOL METHODS ====================
    
    def add_document(
        self, 
        content: str, 
        title: str, 
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Add a new document to the RAG system
        
        Args:
            content: Document text content
            title: Document title
            metadata: Optional metadata (author, date, type, etc.)
            
        Returns:
            Result dictionary with doc_id and status
        """
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
        
        # Generate embeddings for each chunk
        chunk_data = []
        for chunk in chunks:
            embedding = self._generate_embedding(chunk["text"])
            chunk_info = {
                "chunk_id": f"{doc_id}_{chunk['chunk_id']}",
                "doc_id": doc_id,
                "text": chunk["text"],
                "embedding": embedding,
                "length": chunk["length"]
            }
            chunk_data.append(chunk_info)
            
            # Save chunk to file
            chunk_file = os.path.join(self.chunks_path, f"{chunk_info['chunk_id']}.json")
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk_info, f, indent=2)
        
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
        
        # Add chunk references to index
        for chunk_info in chunk_data:
            self.index["chunks"][chunk_info["chunk_id"]] = {
                "doc_id": doc_id,
                "chunk_file": f"{chunk_info['chunk_id']}.json"
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
        Search documents using semantic similarity (RAG retrieval)
        
        Args:
            query: Search query
            top_k: Number of top results to return
            doc_filter: Optional document ID to search within
            
        Returns:
            Search results with relevant chunks
        """
        # Generate query embedding
        query_embedding = genai.embed_content(
            model=self.embedding_model,
            content=query,
            task_type="retrieval_query"
        )['embedding']
        
        # Score all chunks
        results = []
        chunk_ids = list(self.index["chunks"].keys())
        
        # Filter by document if specified
        if doc_filter:
            chunk_ids = [cid for cid in chunk_ids 
                        if self.index["chunks"][cid]["doc_id"] == doc_filter]
        
        for chunk_id in chunk_ids:
            chunk_info = self.index["chunks"][chunk_id]
            chunk_file = os.path.join(self.chunks_path, chunk_info["chunk_file"])
            
            if os.path.exists(chunk_file):
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)
                
                similarity = self._cosine_similarity(
                    query_embedding, 
                    chunk_data["embedding"]
                )
                
                results.append({
                    "chunk_id": chunk_id,
                    "doc_id": chunk_data["doc_id"],
                    "text": chunk_data["text"],
                    "similarity": similarity,
                    "doc_title": self.index["documents"][chunk_data["doc_id"]]["title"]
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        top_results = results[:top_k]
        
        return {
            "success": True,
            "query": query,
            "results_count": len(top_results),
            "total_searched": len(results),
            "results": top_results
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
        
        # Search relevant chunks in this document
        search_results = self.search_documents(question, top_k=3, doc_filter=doc_id)
        
        if not search_results["results"]:
            return {
                "success": False,
                "message": "No relevant content found in document"
            }
        
        # Build context from top chunks
        context = "\n\n---\n\n".join([r["text"] for r in search_results["results"]])
        
        # Generate answer using Gemini
        prompt = f"""Based on the following document excerpts, answer the question accurately.

DOCUMENT: {self.index["documents"][doc_id]["title"]}

RELEVANT EXCERPTS:
{context}

QUESTION: {question}

Provide a clear, accurate answer based ONLY on the excerpts above. If the answer is not in the excerpts, say so clearly.

ANSWER:"""
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            return {
                "success": False,
                "message": f"Error generating answer: {str(e)}"
            }
        
        return {
            "success": True,
            "doc_id": doc_id,
            "doc_title": self.index["documents"][doc_id]["title"],
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "chunk_id": r["chunk_id"],
                    "similarity": r["similarity"],
                    "preview": r["text"][:200] + "..."
                }
                for r in search_results["results"]
            ]
        }
    
    def list_documents(self) -> Dict[str, Any]:
        """
        List all documents in the system
        
        Returns:
            List of documents with metadata
        """
        documents = []
        for doc_id, doc_info in self.index["documents"].items():
            documents.append({
                "doc_id": doc_id,
                "title": doc_info["title"],
                "added_at": doc_info["added_at"],
                "chunks": doc_info["chunk_count"],
                "words": doc_info["word_count"],
                "metadata": doc_info.get("metadata", {})
            })
        
        return {
            "success": True,
            "count": len(documents),
            "documents": documents
        }
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Get full document content and metadata
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document information
        """
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
        
        doc_info = self.index["documents"][doc_id]
        
        return {
            "success": True,
            "doc_id": doc_id,
            "title": doc_info["title"],
            "content": content,
            "metadata": doc_info.get("metadata", {}),
            "added_at": doc_info["added_at"],
            "stats": {
                "chunks": doc_info["chunk_count"],
                "characters": doc_info["char_count"],
                "words": doc_info["word_count"]
            }
        }
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Delete a document and its chunks
        
        Args:
            doc_id: Document ID
            
        Returns:
            Deletion status
        """
        if doc_id not in self.index["documents"]:
            return {
                "success": False,
                "message": f"Document {doc_id} not found"
            }
        
        # Delete document file
        doc_file = os.path.join(self.docs_path, f"{doc_id}.txt")
        if os.path.exists(doc_file):
            os.remove(doc_file)
        
        # Delete chunk files
        chunks_to_delete = [cid for cid, info in self.index["chunks"].items() 
                           if info["doc_id"] == doc_id]
        
        for chunk_id in chunks_to_delete:
            chunk_file = os.path.join(
                self.chunks_path, 
                self.index["chunks"][chunk_id]["chunk_file"]
            )
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
            del self.index["chunks"][chunk_id]
        
        # Remove from index
        title = self.index["documents"][doc_id]["title"]
        del self.index["documents"][doc_id]
        self._save_index()
        
        return {
            "success": True,
            "doc_id": doc_id,
            "title": title,
            "chunks_deleted": len(chunks_to_delete),
            "message": f"Document '{title}' deleted successfully"
        }
    
    def compare_documents(
        self, 
        doc_id1: str, 
        doc_id2: str
    ) -> Dict[str, Any]:
        """
        Compare two documents using LLM
        
        Args:
            doc_id1: First document ID
            doc_id2: Second document ID
            
        Returns:
            Comparison analysis
        """
        doc1 = self.get_document(doc_id1)
        doc2 = self.get_document(doc_id2)
        
        if not doc1["success"] or not doc2["success"]:
            return {
                "success": False,
                "message": "One or both documents not found"
            }
        
        prompt = f"""Compare these two legal documents and provide a detailed analysis.

DOCUMENT 1: {doc1['title']}
{doc1['content'][:2000]}

DOCUMENT 2: {doc2['title']}
{doc2['content'][:2000]}

Provide comparison covering:
1. Similarities
2. Key Differences
3. Conflicting Provisions
4. Complementary Aspects
5. Overall Assessment

COMPARISON:"""
        
        try:
            response = self.model.generate_content(prompt)
            comparison = response.text
        except Exception as e:
            return {
                "success": False,
                "message": f"Error generating comparison: {str(e)}"
            }
        
        return {
            "success": True,
            "doc1": {"id": doc_id1, "title": doc1["title"]},
            "doc2": {"id": doc_id2, "title": doc2["title"]},
            "comparison": comparison
        }
    
    def semantic_search_all(
        self, 
        query: str, 
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Semantic search across all documents with grouped results
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            Grouped search results by document
        """
        search_results = self.search_documents(query, top_k=top_k)
        
        # Group by document
        by_document = {}
        for result in search_results["results"]:
            doc_id = result["doc_id"]
            if doc_id not in by_document:
                by_document[doc_id] = {
                    "doc_id": doc_id,
                    "title": result["doc_title"],
                    "chunks": [],
                    "max_similarity": 0
                }
            
            by_document[doc_id]["chunks"].append({
                "text": result["text"][:200] + "...",
                "similarity": result["similarity"]
            })
            
            by_document[doc_id]["max_similarity"] = max(
                by_document[doc_id]["max_similarity"],
                result["similarity"]
            )
        
        # Sort documents by max similarity
        documents = sorted(
            by_document.values(), 
            key=lambda x: x["max_similarity"], 
            reverse=True
        )
        
        return {
            "success": True,
            "query": query,
            "documents_found": len(documents),
            "documents": documents
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            Statistics about documents and chunks
        """
        total_words = sum(
            doc["word_count"] 
            for doc in self.index["documents"].values()
        )
        total_chunks = sum(
            doc["chunk_count"] 
            for doc in self.index["documents"].values()
        )
        
        return {
            "success": True,
            "total_documents": len(self.index["documents"]),
            "total_chunks": total_chunks,
            "total_words": total_words,
            "storage_path": self.storage_path,
            "documents": [
                {
                    "title": doc["title"],
                    "chunks": doc["chunk_count"],
                    "words": doc["word_count"]
                }
                for doc in self.index["documents"].values()
            ]
        }
