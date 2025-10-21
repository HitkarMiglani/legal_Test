"""
Embedding generator module for LuminaryAI
"""
import os
from typing import List, Dict
import google.generativeai as genai
from config import Config
import numpy as np

class EmbeddingGenerator:
    """Generate embeddings for text using Google's Gemini API"""
    
    def __init__(self):
        """Initialize the embedding generator"""
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model_name = Config.EMBEDDING_MODEL
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a query
        
        Args:
            query: Search query
            
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            raise Exception(f"Error generating query embedding: {str(e)}")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score between -1 and 1
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_most_similar(
        self, 
        query_embedding: List[float], 
        document_embeddings: List[Dict[str, any]], 
        top_k: int = 5
    ) -> List[Dict[str, any]]:
        """
        Find most similar documents to a query
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: List of dicts with 'embedding' and 'metadata'
            top_k: Number of top results to return
            
        Returns:
            List of most similar documents with similarity scores
        """
        similarities = []
        
        for doc in document_embeddings:
            similarity = self.cosine_similarity(query_embedding, doc['embedding'])
            similarities.append({
                'similarity': similarity,
                'metadata': doc.get('metadata', {}),
                'text': doc.get('text', '')
            })
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
