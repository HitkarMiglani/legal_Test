"""
Legal retriever module for Indian Kanoon API integration
"""
import requests
from typing import List, Dict, Optional
from config import Config
import json

class LegalRetriever:
    """Retrieve legal cases and information from Indian Kanoon API"""
    
    def __init__(self):
        self.base_url = Config.INDIAN_KANOON_BASE_URL
        self.api_key = Config.INDIAN_KANOON_API_KEY
    
    def search_cases(
        self, 
        query: str, 
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for legal cases
        
        Args:
            query: Search query
            limit: Maximum number of results
            filters: Optional filters (court, date range, etc.)
            
        Returns:
            List of case results
        """
        try:
            # Note: This is a placeholder implementation
            # Actual Indian Kanoon API endpoints may differ
            endpoint = f"{self.base_url}/search"
            
            params = {
                'q': query,
                'limit': limit
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            if filters:
                params.update(filters)
            
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                print(f"API request failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching cases: {str(e)}")
            return []
    
    def get_case_details(self, case_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific case
        
        Args:
            case_id: Case identifier
            
        Returns:
            Case details or None
        """
        try:
            endpoint = f"{self.base_url}/case/{case_id}"
            
            params = {}
            if self.api_key:
                params['api_key'] = self.api_key
            
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching case details: {str(e)}")
            return None
    
    def search_by_citation(self, citation: str) -> Optional[Dict]:
        """
        Search for a case by citation
        
        Args:
            citation: Legal citation
            
        Returns:
            Case information or None
        """
        try:
            endpoint = f"{self.base_url}/citation"
            
            params = {
                'citation': citation
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Error searching by citation: {str(e)}")
            return None
    
    def get_related_cases(self, case_id: str, limit: int = 5) -> List[Dict]:
        """
        Get related cases for a given case
        
        Args:
            case_id: Case identifier
            limit: Maximum number of related cases
            
        Returns:
            List of related cases
        """
        try:
            endpoint = f"{self.base_url}/related/{case_id}"
            
            params = {
                'limit': limit
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('related', [])
            else:
                return []
                
        except Exception as e:
            print(f"Error fetching related cases: {str(e)}")
            return []
    
    def extract_legal_concepts(self, text: str) -> List[str]:
        """
        Extract legal concepts from text (local processing)
        
        Args:
            text: Input text
            
        Returns:
            List of legal concepts
        """
        # Common Indian legal terms and concepts
        legal_keywords = [
            'Section', 'Act', 'Article', 'Constitution', 'IPC', 'CrPC', 'CPC',
            'plaintiff', 'defendant', 'appellant', 'respondent', 'petition',
            'writ', 'PIL', 'FIR', 'chargesheet', 'bail', 'conviction',
            'acquittal', 'appeal', 'revision', 'Supreme Court', 'High Court'
        ]
        
        found_concepts = []
        text_lower = text.lower()
        
        for keyword in legal_keywords:
            if keyword.lower() in text_lower:
                found_concepts.append(keyword)
        
        return found_concepts
    
    def format_case_summary(self, case_data: Dict) -> str:
        """
        Format case data into a readable summary
        
        Args:
            case_data: Case information dictionary
            
        Returns:
            Formatted summary string
        """
        summary = f"Case: {case_data.get('title', 'N/A')}\n"
        summary += f"Court: {case_data.get('court', 'N/A')}\n"
        summary += f"Date: {case_data.get('date', 'N/A')}\n"
        summary += f"Citation: {case_data.get('citation', 'N/A')}\n\n"
        
        if 'summary' in case_data:
            summary += f"Summary: {case_data['summary']}\n"
        
        return summary
