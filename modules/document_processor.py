"""
Document processing module for LuminaryAI
"""
import os
import hashlib
from typing import Dict, Optional
from pdfminer.high_level import extract_text as extract_pdf_text
import docx2txt
from PyPDF2 import PdfReader
import io

class DocumentProcessor:
    """Process and extract text from various document formats"""
    
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    
    def __init__(self, upload_folder: str = 'uploads'):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def get_file_hash(self, file_content: bytes) -> str:
        """Generate SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Try pdfminer first
            text = extract_pdf_text(file_path)
            if text.strip():
                return text
            
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            text = docx2txt.process(file_path)
            return text
        except Exception as e:
            raise Exception(f"Error extracting DOCX text: {str(e)}")
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    
    def process_document(self, file_path: str, file_type: str) -> Dict[str, any]:
        """
        Process document and extract text
        
        Returns:
            Dict with 'text', 'metadata', and 'chunks'
        """
        if file_type == 'pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_type == 'docx':
            text = self.extract_text_from_docx(file_path)
        elif file_type == 'txt':
            text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Clean text
        text = self.clean_text(text)
        
        # Generate metadata
        metadata = {
            'char_count': len(text),
            'word_count': len(text.split()),
            'file_type': file_type
        }
        
        # Split into chunks for processing
        chunks = self.chunk_text(text)
        
        return {
            'text': text,
            'metadata': metadata,
            'chunks': chunks
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        # Remove multiple spaces
        import re
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
        """
        Split text into overlapping chunks for embedding
        
        Args:
            text: Input text
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence ending
                for punct in ['. ', '! ', '? ', '\n']:
                    last_punct = text.rfind(punct, start, end)
                    if last_punct != -1:
                        end = last_punct + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < text_length else text_length
        
        return chunks
    
    def save_uploaded_file(self, file, filename: str) -> str:
        """Save uploaded file and return path"""
        file_path = os.path.join(self.upload_folder, filename)
        file.save(file_path)
        return file_path
    
    def get_file_extension(self, filename: str) -> str:
        """Get file extension"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
