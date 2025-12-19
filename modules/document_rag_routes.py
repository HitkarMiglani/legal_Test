"""
API Routes for Document RAG Tool
Provides REST endpoints for LLM-based document management
"""
from flask import Blueprint, request, jsonify
from modules.auth import auth_manager
import os

# Create blueprint
rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')

# RAG tool instance will be injected from app.py
rag_tool = None

def init_rag_routes(rag_tool_instance):
    """Initialize routes with the shared RAG tool instance"""
    global rag_tool
    rag_tool = rag_tool_instance

@rag_bp.route('/documents', methods=['POST'])
@auth_manager.token_required
def add_document():
    """
    Add a new document to RAG system
    
    Body:
    {
        "content": "document text",
        "title": "document title",
        "metadata": {"key": "value"}
    }
    """
    if rag_tool is None:
        return jsonify({'error': 'RAG tool not initialized'}), 503
        
    try:
        data = request.get_json()
        
        content = data.get('content')
        title = data.get('title')
        metadata = data.get('metadata', {})
        
        if not content or not title:
            return jsonify({'error': 'Content and title are required'}), 400
        
        # Add user info to metadata
        metadata['user_id'] = request.current_user['user_id']
        metadata['username'] = request.current_user['username']
        
        result = rag_tool.add_document(content, title, metadata)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/documents', methods=['GET'])
@auth_manager.token_required
def list_documents():
    """List all documents in RAG system"""
    try:
        result = rag_tool.list_documents()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/documents/<doc_id>', methods=['GET'])
@auth_manager.token_required
def get_document(doc_id):
    """Get full document by ID"""
    try:
        result = rag_tool.get_document(doc_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/documents/<doc_id>', methods=['DELETE'])
@auth_manager.token_required
def delete_document(doc_id):
    """Delete a document"""
    try:
        result = rag_tool.delete_document(doc_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/search', methods=['POST'])
@auth_manager.token_required
def search_documents():
    """
    Search documents using RAG
    
    Body:
    {
        "query": "search query",
        "top_k": 5,
        "doc_filter": "optional_doc_id"
    }
    """
    try:
        data = request.get_json()
        
        query = data.get('query')
        top_k = data.get('top_k', 5)
        doc_filter = data.get('doc_filter')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        result = rag_tool.search_documents(query, top_k, doc_filter)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/documents/<doc_id>/query', methods=['POST'])
@auth_manager.token_required
def query_document(doc_id):
    """
    Ask a question about a specific document
    
    Body:
    {
        "question": "your question"
    }
    """
    if rag_tool is None:
        return jsonify({'error': 'RAG tool not initialized'}), 503
        
    try:
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        result = rag_tool.query_document(doc_id, question)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/search/semantic', methods=['POST'])
@auth_manager.token_required
def semantic_search():
    """
    Semantic search across all documents
    
    Body:
    {
        "query": "search query",
        "top_k": 10
    }
    """
    try:
        data = request.get_json()
        
        query = data.get('query')
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        result = rag_tool.semantic_search_all(query, top_k)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/documents/compare', methods=['POST'])
@auth_manager.token_required
def compare_documents():
    """
    Compare two documents
    
    Body:
    {
        "doc_id1": "first_doc_id",
        "doc_id2": "second_doc_id"
    }
    """
    try:
        data = request.get_json()
        
        doc_id1 = data.get('doc_id1')
        doc_id2 = data.get('doc_id2')
        
        if not doc_id1 or not doc_id2:
            return jsonify({'error': 'Both doc_id1 and doc_id2 are required'}), 400
        
        result = rag_tool.compare_documents(doc_id1, doc_id2)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/statistics', methods=['GET'])
@auth_manager.token_required
def get_statistics():
    """Get RAG system statistics"""
    try:
        result = rag_tool.get_statistics()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Register the blueprint in your main app.py:
# from modules.document_rag_routes import rag_bp
# app.register_blueprint(rag_bp)
