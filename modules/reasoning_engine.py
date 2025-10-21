"""
Gemini reasoning engine for advanced legal analysis
"""
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
    
    def analyze_legal_document(
        self, 
        document_text: str, 
        analysis_type: str = "comprehensive"
    ) -> Dict[str, any]:
        """
        Perform deep analysis of a legal document
        
        Args:
            document_text: Text of the legal document
            analysis_type: Type of analysis (comprehensive, summary, specific)
            
        Returns:
            Analysis results dictionary
        """
        prompts = {
            "comprehensive": f"""
Analyze this legal document comprehensively:

{document_text}

Provide a detailed analysis covering:
1. Document Type and Purpose
2. Key Legal Provisions
3. Rights and Obligations
4. Potential Issues or Concerns
5. Relevant Indian Laws
6. Recommendations

Format your response as JSON with these keys.
""",
            "summary": f"""
Provide a concise summary of this legal document:

{document_text}

Include:
- Main purpose
- Key parties
- Critical terms
- Important dates

Keep it brief and clear.
""",
            "specific": f"""
Extract specific legal elements from this document:

{document_text}

Identify:
1. Legal sections/articles referenced
2. Case law citations
3. Statutory provisions
4. Contractual obligations
5. Jurisdictional information
"""
        }
        
        prompt = prompts.get(analysis_type, prompts["comprehensive"])
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return {
                'success': True,
                'analysis': response.text,
                'type': analysis_type
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
        
        instruction = role_instructions.get(role, role_instructions["public"])
        
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
