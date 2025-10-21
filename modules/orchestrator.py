"""
LangChain orchestrator for LuminaryAI
"""
from langchain_classic.chains import LLMChain 
from langchain_classic.prompts import PromptTemplate
from langchain_classic.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, List, Optional
from config import Config

class LangChainOrchestrator:
    """Orchestrate LangChain components for legal analysis"""
    
    def __init__(self):
        """Initialize the orchestrator"""
        self.llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=Config.TEMPERATURE,
            max_output_tokens=Config.MAX_TOKENS
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    
    def create_legal_analysis_chain(self, role: str = "public") -> LLMChain:
        """
        Create a chain for legal document analysis
        
        Args:
            role: User role (lawyer, student, public)
            
        Returns:
            LLMChain configured for legal analysis
        """
        # Role-specific prompts
        role_context = {
            "lawyer": "You are assisting a practicing lawyer. Provide detailed legal analysis with case law references, precedents, and technical legal terminology.",
            "student": "You are assisting a law student. Explain legal concepts clearly with examples, and include educational context.",
            "public": "You are assisting a member of the public. Explain legal matters in simple, accessible language without excessive jargon."
        }
        
        context = role_context.get(role, role_context["public"])
        
        template = f"""
{context}

You are LuminaryAI, an expert on Indian law and legal documents.

Context Information:
{{context}}

Document/Query:
{{query}}

Previous Conversation:
{{chat_history}}

Please provide a comprehensive legal analysis addressing:
1. Main legal issues and concepts
2. Relevant Indian laws, sections, and articles
3. Key interpretations and implications
4. Practical recommendations (if applicable)

Analysis:
"""
        
        prompt = PromptTemplate(
            input_variables=["context", "query", "chat_history"],
            template=template
        )
        
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory
        )
        
        return chain
    
    def create_document_qa_chain(self) -> LLMChain:
        """Create a chain for document Q&A"""
        template = """
You are LuminaryAI, an AI assistant specialized in Indian legal documents.

Document Context:
{document_context}

Question: {question}

Previous Conversation:
{chat_history}

Provide a clear, accurate answer based on the document content. 
If the information is not in the document, clearly state that.

Answer:
"""
        
        prompt = PromptTemplate(
            input_variables=["document_context", "question", "chat_history"],
            template=template
        )
        
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory
        )
        
        return chain
    
    def create_case_summary_chain(self) -> LLMChain:
        """Create a chain for summarizing legal cases"""
        template = """
You are LuminaryAI, an expert in summarizing Indian legal cases.

Case Information:
{case_info}

Create a structured summary with:
1. Case Title and Citation
2. Court and Date
3. Key Facts
4. Legal Issues
5. Court's Decision
6. Key Legal Principles
7. Significance

Summary:
"""
        
        prompt = PromptTemplate(
            input_variables=["case_info"],
            template=template
        )
        
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt
        )
        
        return chain
    
    def create_legal_research_chain(self) -> LLMChain:
        """Create a chain for legal research assistance"""
        template = """
You are LuminaryAI, a legal research assistant for Indian law.

Research Query: {query}

Available Context:
{context}

Relevant Cases:
{cases}

Provide comprehensive research findings including:
1. Relevant legal provisions
2. Key precedents and case law
3. Legal interpretations
4. Practical implications
5. Further research suggestions

Research Findings:
"""
        
        prompt = PromptTemplate(
            input_variables=["query", "context", "cases"],
            template=template
        )
        
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt
        )
        
        return chain
    
    def analyze_document(
        self, 
        document_text: str, 
        user_query: str, 
        role: str = "public",
        additional_context: str = ""
    ) -> str:
        """
        Analyze a legal document with user query
        
        Args:
            document_text: Text content of the document
            user_query: User's question or analysis request
            role: User role
            additional_context: Any additional context
            
        Returns:
            Analysis result
        """
        chain = self.create_legal_analysis_chain(role)
        
        context = f"Document Content:\n{document_text}\n\n{additional_context}"
        
        result = chain.invoke({
            "context": context,
            "query": user_query,
            "chat_history": ""
        })
        
        return result.get("text", "")
    
    def answer_question(
        self, 
        document_context: str, 
        question: str
    ) -> str:
        """
        Answer a question about a document
        
        Args:
            document_context: Context from the document
            question: User's question
            
        Returns:
            Answer
        """
        chain = self.create_document_qa_chain()
        
        result = chain.invoke({
            "document_context": document_context,
            "question": question,
            "chat_history": ""
        })
        
        return result.get("text", "")
    
    def summarize_case(self, case_info: str) -> str:
        """
        Summarize a legal case
        
        Args:
            case_info: Information about the case
            
        Returns:
            Structured summary
        """
        chain = self.create_case_summary_chain()
        
        result = chain.invoke({
            "case_info": case_info
        })
        
        return result.get("text", "")
    
    def conduct_research(
        self, 
        query: str, 
        context: str = "", 
        cases: List[Dict] = None
    ) -> str:
        """
        Conduct legal research
        
        Args:
            query: Research query
            context: Additional context
            cases: List of relevant cases
            
        Returns:
            Research findings
        """
        chain = self.create_legal_research_chain()
        
        cases_str = ""
        if cases:
            for i, case in enumerate(cases, 1):
                cases_str += f"\n{i}. {case.get('title', 'N/A')}\n"
                cases_str += f"   {case.get('summary', '')}\n"
        
        result = chain.invoke({
            "query": query,
            "context": context,
            "cases": cases_str or "No specific cases provided."
        })
        
        return result.get("text", "")
