"""
LangChain Tool Wrapper for Document RAG Tool
Makes the RAG tool accessible to LLMs via LangChain
Works with ChromaDBRAGTool (ChromaDB vector store with local embeddings)
"""
from typing import Optional, Type, Dict, Any
from langchain.tools import BaseTool
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field


# ==================== INPUT SCHEMAS ====================

class AddDocumentInput(BaseModel):
    """Input schema for adding a document"""
    content: str = Field(description="The full text content of the document")
    title: str = Field(description="A descriptive title for the document")
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional metadata as key-value pairs (e.g., {'type': 'contract', 'date': '2025-01-15'})"
    )


class SearchDocumentsInput(BaseModel):
    """Input schema for searching documents"""
    query: str = Field(description="The search query to find relevant document chunks")
    top_k: int = Field(
        default=5,
        description="Number of top results to return (default: 5)"
    )
    doc_filter: Optional[str] = Field(
        default=None,
        description="Optional document ID to search within only that document"
    )


class QueryDocumentInput(BaseModel):
    """Input schema for querying a specific document"""
    doc_id: str = Field(description="The document ID to query")
    question: str = Field(description="The question to ask about the document")


class GetDocumentInput(BaseModel):
    """Input schema for getting a document"""
    doc_id: str = Field(description="The document ID to retrieve")


class DeleteDocumentInput(BaseModel):
    """Input schema for deleting a document"""
    doc_id: str = Field(description="The document ID to delete")


class CompareDocumentsInput(BaseModel):
    """Input schema for comparing documents"""
    doc_id1: str = Field(description="The first document ID")
    doc_id2: str = Field(description="The second document ID")


class SemanticSearchInput(BaseModel):
    """Input schema for semantic search across all documents"""
    query: str = Field(description="The search query")
    top_k: int = Field(
        default=10,
        description="Number of top results to return (default: 10)"
    )


# ==================== LANGCHAIN TOOLS ====================

class AddDocumentTool(BaseTool):
    """Tool for adding a document to the RAG system"""
    
    name: str = "add_document"
    description: str = """
    Add a new document to the RAG system for future retrieval and querying.
    Use this when you need to store a legal document, contract, or any text for later reference.
    
    The document will be:
    - Split into chunks
    - Embedded using Gemini
    - Stored with metadata
    - Made searchable
    
    Returns: document ID and status
    """
    args_schema: Type[BaseModel] = AddDocumentInput
    rag_tool: Any = None
    
    def __init__(self, rag_tool: Any):
        super().__init__()
        self.rag_tool = rag_tool
    
    def _run(
        self,
        content: str,
        title: str,
        metadata: Optional[Dict[str, str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Add a document to the RAG system"""
        result = self.rag_tool.add_document(content, title, metadata)
        
        if result["success"]:
            return f"✓ Document added successfully!\n" \
                   f"- Title: {result['title']}\n" \
                   f"- Document ID: {result['doc_id']}\n" \
                   f"- Chunks created: {result['chunks_created']}\n" \
                   f"- Message: {result['message']}"
        else:
            return f"✗ Failed to add document: {result['message']}"


class SearchDocumentsTool(BaseTool):
    """Tool for semantic search across documents"""
    
    name: str = "search_documents"
    description: str = """
    Search for relevant information across all documents using semantic similarity.
    Use this to find specific clauses, terms, or concepts in documents.
    
    The search uses embeddings to find semantically similar content, not just keyword matching.
    
    Returns: Top matching chunks with similarity scores and source documents
    """
    args_schema: Type[BaseModel] = SearchDocumentsInput
    rag_tool: Any = None
    
    def __init__(self, rag_tool: Any):
        super().__init__()
        self.rag_tool = rag_tool
    
    def _run(
        self,
        query: str,
        top_k: int = 5,
        doc_filter: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Search documents using semantic similarity"""
        result = self.rag_tool.search_documents(query, top_k, doc_filter)
        
        if not result["success"]:
            return f"✗ Search failed: {result.get('message', 'Unknown error')}"
        
        if not result["results"]:
            return f"No results found for query: '{query}'"
        
        output = f"Found {result['results_count']} relevant chunks for: '{query}'\n\n"
        
        for i, r in enumerate(result["results"], 1):
            output += f"{i}. Document: {r['doc_title']}\n"
            output += f"   Similarity: {r['similarity']:.4f}\n"
            output += f"   Text: {r['text'][:200]}...\n\n"
        
        return output


class QueryDocumentTool(BaseTool):
    """Tool for asking questions about a specific document"""
    
    name: str = "query_document"
    description: str = """
    Ask a question about a specific document and get an AI-generated answer based on the document content.
    Use this when you need to extract specific information from a known document.
    
    The tool will:
    - Find relevant chunks in the document
    - Use those chunks as context
    - Generate an accurate answer using LLM
    - Cite the sources used
    
    Returns: Answer to the question with source citations
    """
    args_schema: Type[BaseModel] = QueryDocumentInput
    rag_tool: Any = None
    
    def __init__(self, rag_tool: Any):
        super().__init__()
        self.rag_tool = rag_tool
    
    def _run(
        self,
        doc_id: str,
        question: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Query a specific document"""
        result = self.rag_tool.query_document(doc_id, question)
        
        if not result["success"]:
            return f"✗ Query failed: {result['message']}"
        
        output = f"Document: {result['doc_title']}\n"
        output += f"Question: {result['question']}\n\n"
        output += f"Answer:\n{result['answer']}\n\n"
        output += f"Sources: {len(result['sources'])} chunks used\n"
        
        for i, source in enumerate(result['sources'], 1):
            output += f"  {i}. Similarity: {source['similarity']:.4f} - {source['preview']}\n"
        
        return output


class ListDocumentsTool(BaseTool):
    """Tool for listing all documents in the system"""
    
    name: str = "list_documents"
    description: str = """
    List all documents currently stored in the RAG system.
    Use this to see what documents are available before searching or querying.
    
    Returns: List of all documents with metadata (title, ID, word count, chunks, etc.)
    """
    rag_tool: Any = None
    
    def __init__(self, rag_tool: Any):
        super().__init__()
        self.rag_tool = rag_tool
    
    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """List all documents"""
        result = self.rag_tool.list_documents()
        
        if not result["success"]:
            return "✗ Failed to list documents"
        
        if result["count"] == 0:
            return "No documents found in the system."
        
        output = f"Found {result['count']} documents:\n\n"
        
        for doc in result["documents"]:
            output += f"📄 {doc['title']}\n"
            output += f"   ID: {doc['doc_id']}\n"
            output += f"   Words: {doc['words']}, Chunks: {doc['chunks']}\n"
            output += f"   Added: {doc['added_at']}\n"
            if doc.get('metadata'):
                output += f"   Metadata: {doc['metadata']}\n"
            output += "\n"
        
        return output


class GetDocumentTool(BaseTool):
    """Tool for retrieving full document content"""
    
    name: str = "get_document"
    description: str = """
    Retrieve the full content of a specific document by its ID.
    Use this when you need to read the entire document.
    
    Returns: Complete document content with metadata and statistics
    """
    args_schema: Type[BaseModel] = GetDocumentInput
    rag_tool: Any = None
    
    def __init__(self, rag_tool: Any):
        super().__init__()
        self.rag_tool = rag_tool
    
    def _run(
        self,
        doc_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Get full document content"""
        result = self.rag_tool.get_document(doc_id)
        
        if not result["success"]:
            return f"✗ Document not found: {result['message']}"
        
        output = f"Document: {result['title']}\n"
        output += f"ID: {result['doc_id']}\n"
        output += f"Added: {result['added_at']}\n"
        output += f"Statistics:\n"
        output += f"  - Words: {result['stats']['words']}\n"
        output += f"  - Characters: {result['stats']['characters']}\n"
        output += f"  - Chunks: {result['stats']['chunks']}\n"
        
        if result.get('metadata'):
            output += f"Metadata: {result['metadata']}\n"
        
        output += f"\nContent:\n{'-'*50}\n{result['content']}\n"
        
        return output


class DeleteDocumentTool(BaseTool):
    """Tool for deleting a document"""
    
    name: str = "delete_document"
    description: str = """
    Delete a document from the RAG system by its ID.
    This will remove the document and all its chunks permanently.
    
    Use with caution - this action cannot be undone.
    
    Returns: Deletion confirmation with details
    """
    args_schema: Type[BaseModel] = DeleteDocumentInput
    rag_tool: Any = None
    
    def __init__(self, rag_tool: Any):
        super().__init__()
        self.rag_tool = rag_tool
    
    def _run(
        self,
        doc_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Delete a document"""
        result = self.rag_tool.delete_document(doc_id)
        
        if not result["success"]:
            return f"✗ Deletion failed: {result['message']}"
        
        return f"✓ Document deleted successfully!\n" \
               f"- Title: {result['title']}\n" \
               f"- Document ID: {result['doc_id']}\n" \
               f"- Chunks deleted: {result['chunks_deleted']}"


class CompareDocumentsTool(BaseTool):
    """Tool for comparing two documents"""
    
    name: str = "compare_documents"
    description: str = """
    Compare two documents and get an AI-generated analysis of their similarities and differences.
    Use this when you need to understand how two contracts, agreements, or documents differ.
    
    The comparison includes:
    - Similarities between documents
    - Key differences
    - Conflicting provisions
    - Complementary aspects
    - Overall assessment
    
    Returns: Detailed comparison analysis
    """
    args_schema: Type[BaseModel] = CompareDocumentsInput
    rag_tool: Any = None
    
    def __init__(self, rag_tool: Any):
        super().__init__()
        self.rag_tool = rag_tool
    
    def _run(
        self,
        doc_id1: str,
        doc_id2: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Compare two documents"""
        result = self.rag_tool.compare_documents(doc_id1, doc_id2)
        
        if not result["success"]:
            return f"✗ Comparison failed: {result['message']}"
        
        output = f"Comparing Documents:\n"
        output += f"Document 1: {result['doc1']['title']} (ID: {result['doc1']['id']})\n"
        output += f"Document 2: {result['doc2']['title']} (ID: {result['doc2']['id']})\n\n"
        output += f"Comparison Analysis:\n{'-'*50}\n{result['comparison']}"
        
        return output


class SemanticSearchAllTool(BaseTool):
    """Tool for semantic search across all documents with grouped results"""
    
    name: str = "semantic_search_all"
    description: str = """
    Perform semantic search across all documents and get results grouped by document.
    Use this to find which documents contain information about a topic.
    
    Unlike regular search, this groups results by document and shows relevance scores.
    Perfect for finding the most relevant documents for a topic.
    
    Returns: Documents ranked by relevance with matching chunks
    """
    args_schema: Type[BaseModel] = SemanticSearchInput
    rag_tool: Any = None
    
    def __init__(self, rag_tool: Any):
        super().__init__()
        self.rag_tool = rag_tool
    
    def _run(
        self,
        query: str,
        top_k: int = 10,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Semantic search across all documents"""
        result = self.rag_tool.semantic_search_all(query, top_k)
        
        if not result["success"]:
            return f"✗ Search failed"
        
        if not result["documents"]:
            return f"No documents found matching: '{query}'"
        
        output = f"Semantic Search Results for: '{query}'\n"
        output += f"Found {result.get('total_docs_found', len(result.get('documents', [])))} relevant documents\n\n"
        
        for i, doc in enumerate(result["documents"], 1):
            output += f"{i}. {doc['title']}\n"
            output += f"   Relevance: {doc['max_similarity']:.4f}\n"
            output += f"   Matching chunks: {doc.get('chunk_count', len(doc.get('top_chunks', [])))}\n"
            
            # Show top 2 chunks
            top_chunks = doc.get('top_chunks', [])
            for j, chunk in enumerate(top_chunks[:2], 1):
                output += f"   Chunk {j}: {chunk['text'][:150]}...\n"
            
            output += "\n"
        
        return output


class GetStatisticsTool(BaseTool):
    """Tool for getting RAG system statistics"""
    
    name: str = "get_statistics"
    description: str = """
    Get statistics about the RAG system including total documents, chunks, and words.
    Use this to understand the current state of the document repository.
    
    Returns: System statistics and summary
    """
    rag_tool: Any = None
    
    def __init__(self, rag_tool: Any):
        super().__init__()
        self.rag_tool = rag_tool
    
    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Get system statistics"""
        result = self.rag_tool.get_statistics()
        
        if not result["success"]:
            return "✗ Failed to get statistics"
        
        output = f"RAG System Statistics:\n{'-'*50}\n"
        output += f"Total Documents: {result['total_documents']}\n"
        output += f"Total Chunks: {result['total_chunks']}\n"
        output += f"Total Words: {result['total_words']:,}\n"
        output += f"Storage Path: {result['storage_path']}\n\n"
        
        if result.get('documents'):
            output += "Document Breakdown:\n"
            for doc in result['documents']:
                output += f"  - {doc['title']}: {doc['words']} words, {doc['chunks']} chunks\n"
        
        return output


# ==================== TOOL FACTORY ====================

def create_document_rag_tools(rag_tool=None, storage_path: str = "chromadb_storage") -> list:
    """
    Create all Document RAG tools for LangChain
    
    Args:
        rag_tool: Optional pre-initialized ChromaDBRAGTool
        storage_path: Path to ChromaDB storage (used if rag_tool not provided)
        
    Returns:
        List of LangChain tools
    """
    # Use provided tool or create default one
    if rag_tool is None:
        from modules.document_rag_chromadb import ChromaDBRAGTool
        rag_tool = ChromaDBRAGTool(storage_path=storage_path, model_name="all-MiniLM-L6-v2")
    
    return [
        AddDocumentTool(rag_tool),
        SearchDocumentsTool(rag_tool),
        QueryDocumentTool(rag_tool),
        ListDocumentsTool(rag_tool),
        GetDocumentTool(rag_tool),
        DeleteDocumentTool(rag_tool),
        CompareDocumentsTool(rag_tool),
        SemanticSearchAllTool(rag_tool),
        GetStatisticsTool(rag_tool)
    ]


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    """
    Example usage with LangChain agent
    """
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_classic.prompts import PromptTemplate
    from config import Config
    
    # Create tools
    tools = create_document_rag_tools()
    
    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model=Config.LLM_MODEL,
        google_api_key=Config.GOOGLE_API_KEY,
        temperature=0.7
    )
    
    # Create prompt
    template = """You are a legal AI assistant with access to document management tools.
    
You can:
- Add documents to the system
- Search for information across documents
- Ask questions about specific documents
- Compare documents
- List and manage documents

Use the tools available to help answer questions and manage legal documents.

Available tools:
{tools}

Tool names: {tool_names}

Question: {input}

Thought: {agent_scratchpad}
"""
    
    prompt = PromptTemplate.from_template(template)
    
    # Create agent
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )
    
    # Example queries
    print("Document RAG Tools initialized!")
    print(f"Available tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description[:100]}...")
