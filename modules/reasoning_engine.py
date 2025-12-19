"""
Gemini reasoning engine for advanced legal analysis
"""
import os
import warnings

# Suppress gRPC/ALTS warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'
warnings.filterwarnings('ignore')

import google.generativeai as genai
from typing import Dict, List, Optional
from config import Config
import json

class GeminiReasoningEngine:
    """Advanced reasoning engine using Gemini LLM"""
    
    def __init__(self):
        """Initialize the reasoning engine"""
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(Config.LLM_MODEL)
        
        # Configure generation parameters
        self.generation_config = {
            'temperature': Config.TEMPERATURE,
            'max_output_tokens': Config.MAX_TOKENS,
            'top_p': 0.8,
            'top_k': 40
        }
        
        # Fast generation config for summaries (reduces timeout risk)
        self.fast_generation_config = {
            'temperature': 0.5,
            'max_output_tokens': 1024,  # Reduced for faster response
            'top_p': 0.8,
            'top_k': 40
        }
    
    def _chunk_document(self, text: str, chunk_size: int = 2000) -> List[str]:
        """
        Split document into chunks for processing
        
        Args:
            text: Document text
            chunk_size: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        paragraphs = text.split('\n')
        current_chunk = ""
        current_length = 0
        
        for paragraph in paragraphs:
            para_length = len(paragraph)
            
            if current_length + para_length + 2 <= chunk_size:
                current_chunk += paragraph + '\n\n'
                current_length += para_length + 2
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
                current_length = para_length + 2
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _extract_key_elements(self, document_text: str) -> Dict[str, any]:
        """
        Extract key elements from document using Gemini
        
        Args:
            document_text: Full document text
            
        Returns:
            Dictionary of extracted elements
        """
        # Limit text for faster extraction
        text_preview = document_text[:2000] if len(document_text) > 2000 else document_text
        
        prompt = f"""
Extract key legal elements from this document and return ONLY valid JSON:

{text_preview}

Extract:
{{
  "document_type": "type of document (contract/agreement/notice/etc)",
  "parties": ["list of parties involved"],
  "key_dates": ["important dates mentioned"],
  "legal_provisions": ["Indian laws/sections referenced"],
  "obligations": ["key obligations or duties"],
  "rights": ["key rights mentioned"],
  "amounts": ["monetary amounts mentioned"],
  "jurisdiction": "legal jurisdiction"
}}

Return ONLY the JSON object, no explanation.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.fast_generation_config
            )
            
            # Try to parse JSON
            text = response.text.strip()
            text = text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except Exception as e:
            # Return empty structure on error to prevent cascade failure
            return {
                "document_type": "unknown",
                "parties": [],
                "key_dates": [],
                "legal_provisions": [],
                "obligations": [],
                "rights": [],
                "amounts": [],
                "jurisdiction": "unknown",
                "error": f"Extraction failed: {str(e)}"
            }
    
    def analyze_legal_document(
        self, 
        document_text: str, 
        analysis_type: str = "comprehensive",
        query: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Perform deep analysis of a legal document using chunk-based Gemini processing
        
        Args:
            document_text: Text of the legal document
            analysis_type: Type of analysis (comprehensive, summary, specific, qa)
            query: Optional specific question about the document
            
        Returns:
            Analysis results dictionary
        """
        
        # For Q&A mode with specific query
        if analysis_type == "qa" and query:
            return self._answer_document_question(document_text, query)
        
        # Extract key elements first
        key_elements = self._extract_key_elements(document_text)
        
        # Split document into chunks for comprehensive analysis
        chunks = self._chunk_document(document_text, chunk_size=2000)
        
        # Analyze based on type
        if analysis_type == "comprehensive":
            return self._comprehensive_analysis(document_text, chunks, key_elements)
        elif analysis_type == "summary":
            return self._summary_analysis(document_text, key_elements)
        elif analysis_type == "specific":
            return self._specific_analysis(document_text, key_elements)
        else:
            return self._comprehensive_analysis(document_text, chunks, key_elements)
    
    def _comprehensive_analysis(
        self, 
        full_text: str, 
        chunks: List[str], 
        key_elements: Dict
    ) -> Dict[str, any]:
        """Comprehensive document analysis using Gemini"""
        
        prompt = f"""
As a legal expert specializing in Indian law, provide a comprehensive analysis of this legal document.

KEY ELEMENTS IDENTIFIED:
{json.dumps(key_elements, indent=2)}

DOCUMENT CONTENT:
{full_text[:4000]}{'...(truncated)' if len(full_text) > 4000 else ''}

Provide a detailed analysis with these sections:

1. DOCUMENT OVERVIEW
   - Type and nature of document
   - Primary purpose
   - Date and parties involved

2. LEGAL FRAMEWORK
   - Applicable Indian laws and statutes
   - Relevant sections and provisions
   - Legal validity and compliance

3. KEY PROVISIONS ANALYSIS
   - Main clauses and terms
   - Rights of each party
   - Obligations and duties
   - Conditions and warranties

4. RISK ASSESSMENT
   - Potential legal risks
   - Ambiguous or problematic clauses
   - Missing provisions
   - Enforceability concerns

5. RECOMMENDATIONS
   - Suggested actions
   - Clauses needing attention
   - Legal precautions
   - Next steps

Format clearly with headers. Be specific and cite relevant Indian laws.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return {
                'success': True,
                'analysis': response.text,
                'type': 'comprehensive',
                'key_elements': key_elements,
                'chunks_analyzed': len(chunks)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _summary_analysis(self, document_text: str, key_elements: Dict) -> Dict[str, any]:
        """Generate concise summary - optimized for speed"""
        
        # Limit document text to prevent timeout (reduced from 5000 to 3000)
        text_preview = document_text[:3000] if len(document_text) > 3000 else document_text
        
        prompt = f"""
Provide a concise executive summary of this legal document:

KEY ELEMENTS:
{json.dumps(key_elements, indent=2)}

DOCUMENT (Preview):
{text_preview}

Summary should include:
- Document type and purpose (1-2 sentences)
- Parties involved
- Key terms and conditions (bullet points)
- Important dates and amounts
- Critical obligations
- Jurisdiction and applicable law

Keep it clear, concise, and actionable.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.fast_generation_config
            )
            
            return {
                'success': True,
                'analysis': response.text,
                'type': 'summary',
                'key_elements': key_elements
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _specific_analysis(self, document_text: str, key_elements: Dict) -> Dict[str, any]:
        """Extract specific legal elements"""
        
        prompt = f"""
Extract and list specific legal elements from this document:

{document_text[:3000]}

Provide detailed lists for:

1. STATUTES AND ACTS REFERENCED
   (List each with full name and relevant sections)

2. CASE LAW CITATIONS
   (If any precedents are mentioned)

3. LEGAL TERMS AND DEFINITIONS
   (Key legal terminology used)

4. CONTRACTUAL CLAUSES
   (Major clauses with brief descriptions)

5. COMPLIANCE REQUIREMENTS
   (Regulatory or legal compliance needed)

6. DISPUTE RESOLUTION
   (How disputes are to be resolved)

7. TERMINATION PROVISIONS
   (Conditions for ending the agreement)

Be precise and cite exact references.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return {
                'success': True,
                'analysis': response.text,
                'type': 'specific',
                'key_elements': key_elements
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _answer_document_question(self, document_text: str, query: str) -> Dict[str, any]:
        """
        Answer specific question about document using Gemini
        Similar to RAG Q&A approach
        """
        
        # Chunk document
        chunks = self._chunk_document(document_text, chunk_size=1500)
        
        # Find most relevant chunks (simple keyword matching)
        query_words = set(query.lower().split())
        chunk_scores = []
        
        for i, chunk in enumerate(chunks):
            chunk_words = set(chunk.lower().split())
            overlap = len(query_words.intersection(chunk_words))
            chunk_scores.append((i, overlap, chunk))
        
        # Sort by relevance and take top 3 chunks
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        relevant_chunks = [chunk for _, _, chunk in chunk_scores[:3]]
        context = "\n\n---\n\n".join(relevant_chunks)
        
        prompt = f"""
Based on the following document excerpts, answer the question accurately and concisely.

DOCUMENT EXCERPTS:
{context}

QUESTION: {query}

Provide a clear answer based ONLY on the document content. If the information is not in the document, state that clearly. Cite specific parts of the document when possible.

ANSWER:
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.4,
                    'max_output_tokens': 1024
                }
            )
            
            return {
                'success': True,
                'analysis': response.text,
                'type': 'qa',
                'query': query,
                'chunks_used': len(relevant_chunks)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def compare_documents(
        self, 
        doc1_text: str, 
        doc2_text: str
    ) -> Dict[str, any]:
        """
        Compare two legal documents
        
        Args:
            doc1_text: First document text
            doc2_text: Second document text
            
        Returns:
            Comparison results
        """
        prompt = f"""
Compare these two legal documents:

Document 1:
{doc1_text[:2000]}

Document 2:
{doc2_text[:2000]}

Provide:
1. Similarities
2. Differences
3. Conflicting provisions
4. Complementary aspects
5. Overall compatibility assessment
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return {
                'success': True,
                'comparison': response.text
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def identify_risks(self, document_text: str) -> Dict[str, any]:
        """
        Identify potential legal risks in a document
        
        Args:
            document_text: Document text to analyze
            
        Returns:
            Risk assessment
        """
        prompt = f"""
Analyze this legal document for potential risks and concerns:

{document_text}

Identify:
1. Legal risks
2. Compliance issues
3. Ambiguous clauses
4. Missing provisions
5. Unfavorable terms

Categorize each risk by severity: HIGH, MEDIUM, LOW
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return {
                'success': True,
                'risk_assessment': response.text
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_query(self, query: str, user_role: str = "public") -> Dict[str, any]:
        """
        Validate if query is legal-related and has sufficient context
        
        Args:
            query: User's query text
            user_role: User's role (lawyer/student/public)
            
        Returns:
            Validation result with suggestions
        """
        prompt = f"""
Analyze this query for legal context validation:

Query: "{query}"
User Type: {user_role}

Determine:
1. Is this a legal question? (yes/no)
2. Is the question clear and specific? (yes/no/needs_clarification)
3. Does it relate to Indian law? (yes/no/unclear)
4. What legal domain does it belong to? (criminal/civil/corporate/constitutional/etc.)
5. Quality score (1-10, where 10 is perfectly clear and legal-specific)

If the query needs improvement or clarity (score < 8), suggest a better rephrased version.
Consider the user's role ({user_role}) when suggesting improvements.

Respond in JSON format:
{{
  "is_legal": true/false,
  "is_clear": "yes/no/needs_clarification",
  "relates_to_indian_law": "yes/no/unclear",
  "legal_domain": "domain_name",
  "quality_score": 1-10,
  "suggestions": "how to improve the query if needed",
  "reiterated_query": "improved version of the query if score < 8",
  "validated": true/false
}}
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Try to parse JSON response
            import json
            try:
                result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
                return result
            except:
                # Fallback if not JSON
                return {
                    'is_legal': True,
                    'is_clear': 'yes',
                    'relates_to_indian_law': 'yes',
                    'legal_domain': 'general',
                    'quality_score': 7,
                    'suggestions': '',
                    'reiterated_query': query,
                    'validated': True,
                    'raw_response': response.text
                }
        except Exception as e:
            return {
                'is_legal': True,
                'is_clear': 'yes',
                'relates_to_indian_law': 'yes',
                'legal_domain': 'general',
                'quality_score': 5,
                'suggestions': '',
                'validated': True,
                'error': str(e)
            }
    
    def generate_semantic_short_answer(
        self, 
        query: str, 
        context: str, 
        role: str = "public",
        max_words: int = 150
    ) -> str:
        """
        Generate concise, semantic-based answer
        
        Args:
            query: User's legal query
            context: Relevant context and information
            role: User role
            max_words: Maximum words in answer
            
        Returns:
            Short, semantic answer
        """
        role_instructions = {
            "lawyer": "Provide a concise, technical response with key legal points.",
            "student": "Provide a brief, educational response with main concepts.",
            "public": "Provide a simple, clear answer in plain language."
        }
        
        instruction = role_instructions.get(role, role_instructions["public"])
        
        prompt = f"""
{instruction}

Query: {query}

Context: {context}

Provide a CONCISE answer (maximum {max_words} words) that:
1. Directly addresses the question
2. Highlights the most important legal point
3. Mentions relevant law/section if applicable
4. Uses clear, semantic language
5. Ends with a brief disclaimer

Be precise and to-the-point. No unnecessary elaboration.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.5,  # Lower temperature for more focused answers
                    'max_output_tokens': max_words * 2,  # Allow some buffer
                    'top_p': 0.7,
                    'top_k': 30
                }
            )
            
            return response.text.strip()
        except Exception as e:
            return f"Unable to generate answer: {str(e)}"
    
    def generate_legal_advice(
        self, 
        query: str, 
        context: str, 
        role: str = "public"
    ) -> str:
        """
        Generate legal advice based on query and context
        
        Args:
            query: User's legal query
            context: Relevant context and information
            role: User role (affects complexity of response)
            
        Returns:
            Legal advice text
        """
        role_instructions = {
            "lawyer": "Provide detailed, technical legal analysis suitable for a practicing lawyer.",
            "student": "Explain clearly with educational context, suitable for a law student.",
            "public": "Use simple, accessible language suitable for the general public."
        }
        
        instruction = role_instructions.get(role, role_instructions["PUBLIC"])
        
        prompt = f"""
{instruction}

Query: {query}

Context: {context}

Provide comprehensive legal guidance addressing the query. Include:
1. Relevant legal provisions under Indian law
2. Applicable precedents
3. Practical recommendations
4. Important disclaimers

Remember: This is general information, not formal legal advice.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text
        except Exception as e:
            return f"Error generating advice: {str(e)}"
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract legal entities from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of extracted entities
        """
        prompt = f"""
Extract legal entities from this text:

{text}

Identify and list:
1. Case names
2. Statutes and acts
3. Sections and articles
4. Courts
5. Legal concepts
6. Parties involved

Format as JSON with these categories as keys.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Try to parse JSON response
            try:
                entities = json.loads(response.text)
            except:
                entities = {'raw_text': response.text}
            
            return entities
        except Exception as e:
            return {'error': str(e)}
    
    def chat_interaction(
        self, 
        messages: List[Dict[str, str]], 
        system_context: str = ""
    ) -> str:
        """
        Handle multi-turn chat interaction
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_context: System context/instructions
            
        Returns:
            Response text
        """
        # Build conversation context
        conversation = ""
        
        if system_context:
            conversation += f"System Context: {system_context}\n\n"
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            conversation += f"{role.capitalize()}: {content}\n\n"
        
        conversation += "Assistant: "
        
        try:
            response = self.model.generate_content(
                conversation,
                generation_config=self.generation_config
            )
            
            return response.text
        except Exception as e:
            return f"Error in chat: {str(e)}"
