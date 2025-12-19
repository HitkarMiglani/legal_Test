"""
Agno-based Intelligent Legal Agent
Uses ChromaDB vector database and Google Gemini
"""
import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from agno.agent import Agent
from agno.knowledge.agent import AgentKnowledge
from agno.vectordb.chroma import ChromaDb
from agno.models.huggingface import HuggingFace
from agno.embedder.google import GeminiEmbedder
from agno.document import Document
from agno.tools import tool

from config import Config
from utils.logger import logger


class LegalAgnoAgent:
    """
    Legal Agent using Agno framework with ChromaDB vector database and Google Gemini
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        collection_name: str = "legal_docs",
        model_id: str = "Qwen/Qwen2.5-7B-Instruct",
        user_role: str = "public"
    ):
        """
        Initialize the Agno-based legal agent
        
        Args:
            storage_path: ChromaDB storage path (default from config)
            collection_name: ChromaDB collection name
            model_id: Google Gemini model to use
            user_role: User role (lawyer, student, public)
        """
        # Database configuration
        self.storage_path = storage_path or self._get_storage_path()
        self.collection_name = collection_name
        self.model_id = model_id
        self.user_role = user_role
        
        # Initialize knowledge base with ChromaDB and Google embeddings
        try:
            self.knowledge = AgentKnowledge(
                vector_db=ChromaDb(
                    collection=self.collection_name,
                    path=self.storage_path,
                    embedder=GeminiEmbedder()
                ),
            )
            logger.info(f"Initialized Agno Knowledge with ChromaDB: {collection_name} at {storage_path}")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {str(e)}")
            raise
        
        # Create custom tools
        # Temporarily disabled due to tool parsing compatibility issues
        # self.tools = self._create_tools()
        self.tools = self._create_tools()  # Empty tools list for now
        
        
        # Initialize agent with role-specific instructions and tools
        self.agent = self._create_agent()
        logger.info(f"Agno Legal Agent initialized for role: {user_role} with knowledge base search enabled")
    
    def _get_storage_path(self) -> str:
        """
        Get ChromaDB storage path from config or environment
        """
        # Try to get from environment first
        storage_path = os.getenv('CHROMA_STORAGE_PATH')
        
        if not storage_path:
            # Use default from config or fallback
            storage_path = getattr(Config, 'CHROMA_DIRECTORY', 'chromadb_storage/agno_legal')
        
        # Ensure directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        logger.info(f"Using ChromaDB storage path: {storage_path}")
        return storage_path
    
    def _create_tools(self) -> List:
        """Create custom tools for the agent"""
        
        @tool
        def search_indian_cases(query: str, max_results: int = 5) -> str:
            """
            Search for relevant Indian legal cases and precedents from the knowledge base.
            
            Args:
                query: The legal query or topic to search for
                max_results: Maximum number of results to return (default 5)
            
            Returns:
                Relevant case law and legal precedents
            """
            try:
                # This will search the ChromaDB knowledge base
                from agno.vectordb.search import SearchType
                results = self.knowledge.vector_db.search(
                    query=query,
                    limit=max_results
                )
                
                if not results:
                    return "No relevant cases found in the knowledge base."
                
                # Format results
                output = f"Found {len(results)} relevant case(s):\n\n"
                for i, result in enumerate(results, 1):
                    content = result.get('content', result.get('document', 'No content'))
                    metadata = result.get('metadata', {})
                    output += f"{i}. {content[:500]}...\n"
                    if metadata:
                        output += f"   Metadata: {metadata}\n"
                    output += "\n"
                
                return output
            except Exception as e:
                logger.error(f"Error searching cases: {str(e)}")
                return f"Error searching knowledge base: {str(e)}"
        
        @tool
        def search_ipc_sections(section_number: str) -> str:
            """
            Search for specific Indian Penal Code (IPC) sections.
            
            Args:
                section_number: IPC section number (e.g., "420", "376", "302")
            
            Returns:
                Details about the IPC section
            """
            try:
                query = f"Indian Penal Code Section {section_number} IPC"
                results = self.knowledge.vector_db.search(
                    query=query,
                    limit=3
                )
                
                if not results:
                    return f"No information found for IPC Section {section_number}. Please consult the Indian Penal Code or a legal professional."
                
                output = f"Information on IPC Section {section_number}:\n\n"
                for result in results:
                    content = result.get('content', result.get('document', ''))
                    output += f"{content}\n\n"
                
                return output
            except Exception as e:
                return f"Error searching IPC section: {str(e)}"
        
        @tool
        def get_legal_procedure(procedure_type: str) -> str:
            """
            Get information about legal procedures in India.
            
            Args:
                procedure_type: Type of procedure (e.g., "filing FIR", "bail application", "appeal")
            
            Returns:
                Step-by-step procedure information
            """
            try:
                query = f"legal procedure {procedure_type} India steps process"
                results = self.knowledge.vector_db.search(
                    query=query,
                    limit=3
                )
                
                if not results:
                    return f"No specific procedure found for '{procedure_type}'. General legal advice: consult a licensed attorney for procedural guidance."
                
                output = f"Legal Procedure for {procedure_type}:\n\n"
                for result in results:
                    content = result.get('content', result.get('document', ''))
                    output += f"{content}\n\n"
                
                return output
            except Exception as e:
                return f"Error retrieving procedure: {str(e)}"
        
        return [search_indian_cases, search_ipc_sections, get_legal_procedure]
    
    def _create_agent(self) -> Agent:
        """
        Create Agno agent with role-specific instructions
        """
        # Role-specific instructions
        role_instructions = {
            "lawyer": [
                "You are assisting a practicing lawyer in India.",
                "Provide detailed legal analysis with comprehensive case law references.",
                "Include relevant sections from Indian Penal Code (IPC), Constitution, and other statutes.",
                "Cite Supreme Court and High Court judgments with proper case citations.",
                "Use precise legal terminology and maintain professional tone.",
                "Highlight procedural requirements, jurisdictional issues, and practical considerations.",
            ],
            "student": [
                "You are assisting a law student in India.",
                "Explain legal concepts clearly with educational context and examples.",
                "Break down complex legal principles into understandable components.",
                "Include landmark cases and their legal significance.",
                "Provide learning resources and suggest further reading when relevant.",
                "Use a teaching approach that builds understanding progressively.",
            ],
            "public": [
                "You are assisting a member of the general public in India.",
                "Use simple, accessible language avoiding complex legal jargon.",
                "Explain legal concepts in layman's terms with practical examples.",
                "Focus on practical implications and actionable steps.",
                "Clarify citizen rights and responsibilities clearly.",
                "Make legal information understandable without oversimplifying.",
            ]
        }
        
        # Get role-specific instructions (default to public)
        instructions = role_instructions.get(self.user_role.lower(), role_instructions["public"])
        
        # Common instructions for all roles
        common_instructions = [
            "Provide legal information based on Indian law and the knowledge base.",
            "Include relevant legal citations, case law, and statutory references when answering.",
            "Always clarify that you're providing general legal information, not professional legal advice.",
            "Recommend consulting with a licensed attorney for specific legal situations.",
            "Be accurate, thorough, and cite sources from the knowledge base.",
            "If information is not in the knowledge base, clearly state that and provide general guidance.",
            "Maintain confidentiality and professional ethics in all responses.",
        ]
        
        # Combine instructions
        all_instructions = instructions + common_instructions
        
        # Get HuggingFace token from environment
        hf_token = os.getenv('HF_TOKEN')
        if not hf_token:
            logger.warning("HF_TOKEN not found in environment. Model requests may fail.")
        
        # Create agent using HuggingFace model with function calling support
        agent = Agent(
            name=f"LegalAdvisor_{self.user_role.capitalize()}",
            knowledge=self.knowledge,
            search_knowledge=True,  # Enable knowledge base search - uses built-in RAG
            tools=self.tools,  # Custom tools disabled due to parsing issues
            model=HuggingFace(
                id=self.model_id,
                api_key=hf_token,
                max_tokens=2048,
                temperature=0.7
            ),
            markdown=True,
            instructions=all_instructions,
            show_tool_calls=True,
            add_datetime_to_instructions=True,
        )
        
        return agent
    
    def add_document_async(
        self,
        content: Optional[str] = None,
        url: Optional[str] = None,
        file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add document to knowledge base
        
        Args:
            content: Text content to add
            url: URL to fetch and add
            file_path: Local file path to add
            metadata: Additional metadata
        
        Returns:
            Result dictionary with success status
        """
        try:
            # Create Document object based on input type
            if url:
                logger.info(f"Adding document from URL: {url}")
                doc = Document(content=url, name=url, meta_data=metadata or {})
                doc.meta_data['source'] = 'url'
            elif file_path:
                logger.info(f"Adding document from file: {file_path}")
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                doc = Document(content=file_content, name=file_path, meta_data=metadata or {})
                doc.meta_data['source'] = 'file'
            elif content:
                logger.info(f"Adding text content ({len(content)} chars)")
                doc = Document(content=content, name='text_content', meta_data=metadata or {})
                doc.meta_data['source'] = 'text'
            else:
                return {
                    'success': False,
                    'error': 'No content, URL, or file_path provided'
                }
            
            # Load document to knowledge base synchronously
            self.knowledge.load_document(document=doc, upsert=True, skip_existing=True)
            
            return {
                'success': True,
                'message': 'Document added to knowledge base',
                'metadata': metadata
            }
        except Exception as e:
            logger.error(f"Error adding document to knowledge base: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_document_sync(
        self,
        content: Optional[str] = None,
        url: Optional[str] = None,
        file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for add_document_async (now synchronous)
        """
        return self.add_document_async(
            content=content,
            url=url,
            file_path=file_path,
            metadata=metadata
        )
    
    def query_async(
        self,
        query: str,
        stream: bool = False,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the agent synchronously (kept name for compatibility)
        
        Args:
            query: User query
            stream: Whether to stream response
            context: Additional context
        
        Returns:
            Response dictionary
        """
        try:
            # Enhance query with context if provided
            enhanced_query = query
            if context:
                enhanced_query = f"{context}\n\nUser Query: {query}"
            
            logger.info(f"Processing query for {self.user_role}: {query[:100]}...")
            
            # Use synchronous run method
            response = self.agent.run(enhanced_query, stream=stream)
            
            # Debug logging
            logger.info(f"Agent response type: {type(response)}")
            logger.info(f"Agent response: {response}")
            
            if stream:
                # Streaming response
                response_text = ""
                for chunk in response:
                    # Handle different chunk types
                    if hasattr(chunk, 'content') and chunk.content:
                        response_text += str(chunk.content)
                    elif hasattr(chunk, 'delta') and hasattr(chunk.delta, 'content') and chunk.delta.content:
                        response_text += str(chunk.delta.content)
                    elif isinstance(chunk, str):
                        response_text += chunk
                
                return {
                    'success': True,
                    'query': query,
                    'response': response_text.strip(),
                    'user_role': self.user_role,
                    'streamed': True,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                # Non-streaming response
                # Extract response text from RunResponse object
                response_text = ""
                
                # Debug what attributes response has
                logger.info(f"Response attributes: {dir(response)}")
                
                if hasattr(response, 'content') and response.content:
                    logger.info("Extracting from response.content")
                    response_text = str(response.content)
                elif hasattr(response, 'messages') and response.messages:
                    
                    # Extract from messages list
                    for msg in response.messages:
                        if hasattr(msg, 'content') and msg.content:
                            response_text += str(msg.content) + "\n"
                elif hasattr(response, 'message') and response.message:
                    response_text = str(response.message)
                elif isinstance(response, dict):
                    response_text = response.get('content', str(response))
                else:
                    logger.info("Falling back to str(response)")
                    response_text = str(response)
                
                # Remove trailing newlines
                response_text = response_text.strip()
                logger.info(f"Final extracted response text length: {len(response_text)}")
                
                return {
                    'success': True,
                    'query': query,
                    'response': response_text,
                    'user_role': self.user_role,
                    'streamed': False,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                'success': False,
                'query': query,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def query_sync(
        self,
        query: str,
        stream: bool = False,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for query_async (now synchronous)
        """
        return self.query_async(
            query=query,
            stream=stream,
            context=context
        )
    
    def print_response(
        self,
        query: str,
        stream: bool = True,
        context: Optional[str] = None
    ):
        """
        Print agent response to console (useful for testing)
        """
        enhanced_query = query
        if context:
            enhanced_query = f"{context}\n\nUser Query: {query}"
        
        # Use run method and print the response
        response = self.agent.run(enhanced_query, stream=stream)
        
        if stream:
            # Stream and print chunks
            for chunk in response:
                # Handle different event types
                if hasattr(chunk, 'content') and chunk.content:
                    print(chunk.content, end='', flush=True)
                elif hasattr(chunk, 'delta') and hasattr(chunk.delta, 'content') and chunk.delta.content:
                    print(chunk.delta.content, end='', flush=True)
            print()  # New line at end
        else:
            # Print complete response
            if hasattr(response, 'content') and response.content:
                print(response.content)
            elif hasattr(response, 'messages') and response.messages:
                for msg in response.messages:
                    if hasattr(msg, 'content') and msg.content:
                        print(msg.content)
            else:
                print(response)
    
    def load_indian_law_documents_async(self, document_urls: List[str]) -> Dict[str, Any]:
        """
        Load multiple Indian law documents into knowledge base
        
        Args:
            document_urls: List of URLs to Indian law PDFs/documents
        
        Returns:
            Summary of loaded documents
        """
        results = {
            'total': len(document_urls),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for url in document_urls:
            try:
                logger.info(f"Loading document: {url}")
                doc = Document(content=url, name=url, meta_data={'source': 'url', 'type': 'indian_law'})
                self.knowledge.load_document(document=doc, upsert=True, skip_existing=True)
                results['successful'] += 1
                results['details'].append({
                    'url': url,
                    'status': 'success'
                })
            except Exception as e:
                logger.error(f"Failed to load {url}: {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'url': url,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results


# Factory function for easy agent creation
def create_legal_agent(
    user_role: str = "public",
    storage_path: Optional[str] = None,
    model_id: str = "Qwen/Qwen2.5-7B-Instruct"
) -> LegalAgnoAgent:
    """
    Create a legal agent instance
    
    Args:
        user_role: User role (lawyer, student, public)
        storage_path: ChromaDB storage path
        model_id: Google Gemini model ID
    
    Returns:
        LegalAgnoAgent instance
    """
    return LegalAgnoAgent(
        storage_path=storage_path,
        user_role=user_role,
        model_id=model_id
    )


# Example usage
if __name__ == "__main__":
    # Create agent
    agent = create_legal_agent(user_role="lawyer")
    
    # Add sample text content (example)
    agent.add_document_async(
        content="Sample legal content: Indian Penal Code Section 420 deals with cheating and dishonestly inducing delivery of property."
    )
    
    # Query the agent
    agent.print_response(
        "What are the legal consequences and criminal penalties for email spoofing in India?",
        stream=True
    )
