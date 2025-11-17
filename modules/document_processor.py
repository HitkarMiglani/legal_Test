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

# OCR imports (optional)
try:
    import pdf2image
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

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
        """Extract text from PDF file with OCR fallback for image-based PDFs"""
        text = ""
        is_image_based = False
        page_count = 0
        
        # Try PyPDF2 first (most reliable for text-based PDFs)
        try:
            print(f"Attempting PyPDF2 extraction for: {file_path}")
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                page_count = len(reader.pages)
                print(f"PDF has {page_count} pages")
                
                # Check if PDF has extractable text
                total_chars = 0
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    char_count = len(page_text.strip())
                    total_chars += char_count
                    print(f"Page {i+1}: {char_count} characters extracted")
                    text += page_text + "\n"
                
                # Detect if this is an image-based PDF
                # Heuristic: Less than 50 characters total suggests image-based
                if total_chars < 50 and page_count > 0:
                    print(f"⚠️  PDF appears to be image-based (only {total_chars} chars for {page_count} pages)")
                    is_image_based = True
                    text = ""
                elif text.strip():
                    print(f"✓ PyPDF2 success: {len(text)} total characters")
                    return text
        except Exception as e:
            print(f"PyPDF2 failed: {str(e)}")
        
        # Fallback to pdfminer (sometimes better for complex PDFs)
        if not is_image_based and not text.strip():
            try:
                print(f"Attempting pdfminer extraction for: {file_path}")
                text = extract_pdf_text(file_path)
                if text.strip() and len(text.strip()) >= 50:
                    print(f"✓ pdfminer success: {len(text)} characters")
                    return text
                elif len(text.strip()) < 50:
                    print(f"⚠️  pdfminer extracted minimal text ({len(text.strip())} chars), likely image-based")
                    is_image_based = True
                    text = ""
            except Exception as e:
                print(f"pdfminer failed: {str(e)}")
        
        # Try OCR if PDF is image-based
        if is_image_based or not text.strip():
            if OCR_AVAILABLE:
                print(f"🔍 Attempting OCR extraction (image-based PDF detected)...")
                try:
                    text = self._extract_text_with_ocr(file_path)
                    if text.strip():
                        print(f"✓ OCR success: {len(text)} characters extracted")
                        return text
                except Exception as ocr_error:
                    print(f"OCR failed: {str(ocr_error)}")
            else:
                print(f"❌ OCR libraries not available. Install with: pip install pdf2image pytesseract pillow")
                print(f"   Also install Tesseract: https://github.com/tesseract-ocr/tesseract")
        
        # If everything fails, provide detailed error
        if is_image_based:
            raise Exception(
                f"PDF is image-based (scanned document with {page_count} pages). "
                f"OCR {'not available - install pdf2image, pytesseract, and Tesseract' if not OCR_AVAILABLE else 'failed'}. "
                f"Please convert to text-based PDF or ensure OCR dependencies are installed."
            )
        else:
            raise Exception(
                f"Could not extract text from PDF. The PDF may be corrupted, empty, or have other issues."
            )
    
    def _extract_text_with_ocr(self, file_path: str) -> str:
        """Extract text from image-based PDF using OCR"""
        if not OCR_AVAILABLE:
            raise Exception("OCR libraries not installed")
        
        try:
            # Convert PDF pages to images
            print(f"Converting PDF to images...")
            images = pdf2image.convert_from_path(file_path)
            print(f"Processing {len(images)} pages with OCR...")
            
            # Extract text from each image
            full_text = ""
            for i, image in enumerate(images):
                print(f"OCR processing page {i+1}/{len(images)}...")
                page_text = pytesseract.image_to_string(image, lang='eng')
                full_text += page_text + "\n\n"
                print(f"  Page {i+1}: {len(page_text.strip())} characters extracted")
            
            return full_text.strip()
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
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
    
    def process_document(self, file_path: str, file_type: str, cached_text: Optional[str] = None, cached_metadata: Optional[Dict] = None) -> Dict[str, any]:
        """
        Process document and extract text (with caching support)
        
        Args:
            file_path: Path to document file
            file_type: Type of file (pdf, docx, txt)
            cached_text: Previously extracted text (if available)
            cached_metadata: Previously generated metadata (if available)
        
        Returns:
            Dict with 'text', 'metadata', and 'chunks'
        """
        # Use cached data if available
        if cached_text and cached_metadata:
            print(f"✨ Using cached text for: {file_path} ({cached_metadata.get('char_count', 0)} chars)")
            text = cached_text
            metadata = cached_metadata
        else:
            print(f"Processing document: {file_path} (type: {file_type})")
            
            if file_type == 'pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_type == 'docx':
                text = self.extract_text_from_docx(file_path)
            elif file_type == 'txt':
                text = self.extract_text_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            print(f"Extracted text length before cleaning: {len(text)}")
            
            # Clean text
            text = self.clean_text(text)
            
            print(f"Text length after cleaning: {len(text)}")
            
            if not text.strip():
                raise Exception("No text content extracted from document. The document may be empty, image-based, or corrupted.")
            
            # Generate metadata
            metadata = {
                'char_count': len(text),
                'word_count': len(text.split()),
                'file_type': file_type
            }
            
            print(f"Document metadata: {metadata}")
        
        # Split into chunks for processing (always regenerate for consistency)
        chunks = self.chunk_text(text)
        
        print(f"Document split into {len(chunks)} chunks")
        if chunks:
            print(f"First chunk preview: {chunks[0][:100]}...")
        
        result = {
            'text': text,
            'metadata': metadata,
            'chunks': chunks
        }
        
        print(f"✅ Document processing complete - returning result with {len(result)} keys")
        return result
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        # Remove multiple spaces but preserve single spaces
        import re
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n\n+', '\n\n', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
        """
        Split text into overlapping chunks for embedding - optimized for speed
        
        Args:
            text: Input text
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        text_length = len(text)
        start = 0
        
        # Fast chunking without sentence boundary detection for speed
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append(chunk)
            
            if end >= text_length:
                break
            
            start = end - overlap
        
        return chunks
    
    def save_uploaded_file(self, file, filename: str) -> str:
        """Save uploaded file and return path"""
        file_path = os.path.join(self.upload_folder, filename)
        file.save(file_path)
        return file_path
    
    def get_file_extension(self, filename: str) -> str:
        """Get file extension"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
