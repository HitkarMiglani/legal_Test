"""
Utility functions for LuminaryAI
"""
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Optional

def generate_hash(content: str) -> str:
    """Generate SHA-256 hash of content"""
    return hashlib.sha256(content.encode()).hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename

def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def extract_sections(text: str) -> List[Dict[str, str]]:
    """Extract legal sections from text"""
    # Pattern for Indian legal sections
    section_pattern = r'Section\s+(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?([^.]+)'
    
    matches = re.finditer(section_pattern, text, re.IGNORECASE)
    
    sections = []
    for match in matches:
        sections.append({
            'section_number': match.group(1),
            'act': match.group(2).strip(),
            'full_text': match.group(0)
        })
    
    return sections

def extract_citations(text: str) -> List[str]:
    """Extract legal citations from text"""
    # Common citation patterns
    patterns = [
        r'\d{4}\s+(?:SCC|SCR|AIR)\s+\d+',  # Supreme Court citations
        r'\(\d{4}\)\s+\d+\s+(?:SCC|SCR)',
        r'AIR\s+\d{4}\s+(?:SC|HC)',
    ]
    
    citations = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        citations.extend(matches)
    
    return list(set(citations))  # Remove duplicates

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def highlight_keywords(text: str, keywords: List[str]) -> str:
    """Highlight keywords in text (for display)"""
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(f"**{keyword}**", text)
    return text

class ResponseFormatter:
    """Format API responses consistently"""
    
    @staticmethod
    def success(data: any, message: str = "Success") -> Dict:
        """Format success response"""
        return {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def error(message: str, code: int = 400, details: any = None) -> Dict:
        """Format error response"""
        response = {
            'success': False,
            'error': message,
            'code': code,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            response['details'] = details
        
        return response
    
    @staticmethod
    def paginate(items: List, page: int = 1, per_page: int = 10) -> Dict:
        """Format paginated response"""
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'items': items[start:end],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }
