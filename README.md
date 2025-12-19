# ⚖️ LuminaryAI — Complete Documentation

> **Intelligent Legal Assistant for Indian Law**  
> Making Indian law understandable, accessible, and intelligent — for lawyers, students, and everyone.

---

## 📚 Table of Contents

1. [Overview & Features](#overview--features)
2. [Installation Guide](#installation-guide)
3. [Architecture & Project Structure](#architecture--project-structure)
4. [Memory System Documentation](#memory-system-documentation)
5. [Document Processing & OCR Setup](#document-processing--ocr-setup)
6. [API Reference](#api-reference)
7. [Simplification Plan](#simplification-plan)
8. [Troubleshooting](#troubleshooting)

---

# Overview & Features

## 🧩 What is LuminaryAI?

LuminaryAI is an **intelligent, proactive legal assistant** that makes case discovery easier and legal information accessible to everyone. Built specifically for the Indian legal system, it serves three distinct user groups with personalized experiences:

👨‍⚖️ **For Lawyers**: Technical legal analysis with detailed case law references  
📚 **For Students**: Educational explanations with clear concept breakdowns  
👥 **For Public**: Simple, accessible legal guidance in plain language

Built using **LangChain, LangGraph, Gemini LLM, ChromaDB RAG, and SQLite**, LuminaryAI offers:

- 🧠 **Persistent Memory System** - Remembers your preferences, chat history, and context across sessions
- 🤖 **Autonomous Agent** - LangGraph-powered agent that intelligently selects and uses tools
- 📚 **Smart Document RAG** - ChromaDB-based semantic search across all your legal documents
- 🎯 **Proactive Assistance** - Context-aware suggestions based on your role and preferences
- ⚡ **Role-Based Responses** - Automatically adapts complexity based on user type
- 🔍 **Intelligent Case Discovery** - Find relevant precedents with semantic matching

All through a modern Streamlit frontend and robust Flask backend with **encrypted user preferences** and **database-backed persistence**.

## 💡 Why LuminaryAI?

### The Problem We Solve

**Traditional Legal Research is:**

- ⏰ **Time-Consuming** - Hours spent searching through case law and statutes
- 🧩 **Complex** - Legal jargon makes information inaccessible to non-lawyers
- 💰 **Expensive** - Professional legal advice is costly for students and public
- 📚 **Overwhelming** - Too much information, difficult to find what's relevant
- 🔄 **Reactive** - Tools wait for you to ask instead of proactively helping

### Our Solution: Intelligent & Proactive Legal Assistance

**LuminaryAI Makes Legal Research:**

- ⚡ **Fast** - Semantic search finds relevant information in seconds
- 💡 **Accessible** - Role-based responses adapt to your understanding level
- 🎯 **Proactive** - Suggests relevant cases and documents before you ask
- 🧠 **Smart** - Learns from your preferences and remembers your context
- 🤝 **Inclusive** - Serves lawyers, students, and public with equal effectiveness

### Key Differentiators

1. **🧠 Persistent Memory** - Unlike ChatGPT, we remember your conversations and preferences across sessions
2. **🎯 Role-Based Intelligence** - Responses automatically adapt to lawyer/student/public expertise levels
3. **📚 Document-Aware** - Combines your uploaded documents with Indian case law for comprehensive answers
4. **🤖 Autonomous Agent** - LangGraph agent intelligently selects tools and executes multi-step workflows
5. **🔍 Proactive Suggestions** - Recommends relevant documents and cases based on context
6. **🇮🇳 India-Specific** - Built specifically for Indian legal system with Indian Kanoon integration

## 🌟 Key Features

### 🧠 Intelligent Memory System

- **💾 Persistent Chat History** - All conversations saved and loaded on login
- **⚙️ User Preferences** - Customize practice area, response style, citation format, and language
- **🔐 Encrypted Storage** - Preferences stored securely using Fernet encryption
- **🎯 Context-Aware Responses** - AI adapts to your preferences automatically
- **📊 Settings Dashboard** - Manage preferences, export data, view chat statistics
- **🔄 Cross-Session Continuity** - Pick up where you left off, every time

### 🤖 LangGraph Autonomous Agent

- **🧩 State-Based Reasoning** - Multi-step autonomous decision making
- **🛠️ 9+ Intelligent Tools** - Document search, case lookup, RAG queries, comparisons
- **🎯 Smart Tool Selection** - Agent chooses the right tools for each query
- **📝 Execution Logging** - Transparent reasoning with iteration tracking
- **⚡ Adaptive Workflows** - Handles complex multi-document operations
- **🔍 Source Attribution** - Every answer cites its sources with confidence scores

### 📚 ChromaDB Document RAG

- **🔍 Semantic Search** - Find relevant document sections across your entire library
- **📄 Multi-Document Support** - Upload PDFs, DOCX, and TXT files
- **🎯 Context-Aware Retrieval** - Combines document content with case law
- **💬 Document Q&A** - Ask specific questions about any document
- **📊 Relevance Scoring** - See exactly how relevant each result is
- **🗂️ UUID-Based Management** - Consistent document tracking across database and vector store
- **🔄 OCR Support** - Handles scanned/image-based PDFs with Tesseract OCR

### ⚡ Role-Based Intelligence

- **👨‍⚖️ Lawyer Mode** - Technical analysis, detailed citations, case law focus
- **📚 Student Mode** - Educational explanations, concept breakdowns, learning context
- **👥 Public Mode** - Simple language, accessible explanations, practical guidance
- **🎨 Adaptive Responses** - Automatically adjusts complexity and terminology
- **📈 Personalized Learning** - Remembers your role and preferences across sessions

### 🔍 Proactive Legal Assistance

- **✨ Query Enhancement** - Automatically improves unclear queries (quality score < 8)
- **🎯 Smart Suggestions** - Recommends relevant documents and cases proactively
- **📋 Context Building** - Combines your documents, preferences, and case law
- **⚡ Real-Time Analysis** - Validates legal queries before processing
- **🔔 Intelligent Notifications** - Alerts when better tools are available for your query

### 🔐 Security & Privacy

- **🔒 Encrypted Preferences** - Fernet encryption for all sensitive data
- **🛡️ JWT Authentication** - Secure token-based auth with bcrypt password hashing
- **👤 User Isolation** - Documents and chat history strictly per-user
- **🔑 API Key Protection** - Environment-based configuration for sensitive keys
- **📊 Audit Logging** - Complete logging of all API interactions

---

# Installation Guide

## 📋 Prerequisites

- Python 3.9+
- Git
- 4GB+ RAM
- Windows, macOS, or Linux

## ⚙️ Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/HitkarMiglani/legal_Test.git
cd Agentic_Law_AI
```

### 2. Create Virtual Environment

**Windows:**

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

**Linux/Mac:**

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file:

```env
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Database
DB_URL=sqlite:///luminary.db

# JWT Secret
JWT_SECRET_KEY=your_random_secret_key_here

# Memory Encryption
ENCRYPTION_KEY=your_fernet_encryption_key_here

# Flask Config
FLASK_ENV=development
FLASK_SECRET_KEY=your_flask_secret_key

# Upload Settings
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=16777216  # 16MB
```

**Generate Keys:**

```python
# Fernet Key
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())

# JWT Secret
import secrets
print(secrets.token_hex(32))
```

### 5. Initialize Database

```bash
python -c "from models import init_db; from config import Config; init_db(Config.DB_URL)"
```

### 6. Run Application

**Option A: Development (Flask + Streamlit)**

Terminal 1 (Backend):

```bash
python app.py
```

Terminal 2 (Frontend):

```bash
streamlit run main.py
```

Or Simply run to start both servers
```bash
./run.ps1
```

**Option B: Production**

```bash
# Using waitress
python run_waitress.py

# Or using gunicorn (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```



### 7. Access Application

- Frontend: http://localhost:8501
- Backend API: http://localhost:5000
- API Status: http://localhost:5000/api/status

## 🔧 Optional: OCR Setup for Image-Based PDFs

If you need to process scanned PDFs, install OCR dependencies:

### Install Python Libraries

```bash
pip install pdf2image pytesseract pillow
```

### Install Tesseract Engine

**Windows:**

1. Download from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run installer (default: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH:
   ```powershell
   $env:Path += ";C:\Program Files\Tesseract-OCR"
   ```

**Linux:**

```bash
sudo apt-get install tesseract-ocr
```

**Mac:**

```bash
brew install tesseract
```

### Verify Installation

```bash
tesseract --version
python -c "import pdf2image, pytesseract; print('OCR ready!')"
```

---

# Architecture & Project Structure

## 🏗️ Technology Stack

### Backend

- **Flask** - REST API framework
- **SQLAlchemy** - ORM and database management
- **SQLite** - Local database (production: PostgreSQL)
- **ChromaDB** - Vector database for semantic search
- **LangChain** - LLM orchestration framework
- **LangGraph** - Agent workflow management

### AI/ML

- **Google Gemini** - Primary LLM (gemini-1.5-flash)
- **Sentence-BERT** - Local embeddings (all-MiniLM-L6-v2)
- **Tesseract OCR** - Image-based PDF extraction (optional)

### Frontend

- **Streamlit** - Interactive web interface
- **Plotly** - Data visualization

### Security

- **PyJWT** - JWT authentication
- **bcrypt** - Password hashing
- **Fernet** - Preference encryption

## 📁 Project Structure

```
Agentic_Law_AI/
├── app.py                    # Flask backend (main API)
├── main.py                   # Streamlit frontend
├── config.py                 # Configuration management
├── models.py                 # Database models (SQLAlchemy)
├── requirements.txt          # Python dependencies
│
├── modules/                  # Core modules
│   ├── __init__.py
│   ├── auth.py              # Authentication & JWT
│   ├── document_processor.py # PDF/DOCX extraction + OCR
│   ├── document_rag_chromadb.py # ChromaDB RAG implementation
│   ├── document_rag_langchain.py # LangChain tool wrappers
│   ├── document_rag_routes.py # Document API routes
│   ├── legal_retriever.py   # Indian Kanoon integration
│   ├── memory_manager.py    # Encrypted preference storage
│   ├── orchestrator.py      # LangGraph agent orchestration
│   └── reasoning_engine.py  # Gemini-based legal analysis
│
├── utils/                    # Utilities
│   ├── __init__.py
│   ├── exceptions.py        # Custom exceptions
│   ├── logger.py            # Logging configuration
│   └── middleware.py        # Request logging & error handling
│
├── uploads/                  # Uploaded documents
├── chromadb_storage/         # ChromaDB vector store
├── logs/                     # Application logs
├── env/                      # Virtual environment
│
└── Documentation Files
    ├── README.md
    ├── MEMORY_FLOW.md
    ├── OCR_SETUP_GUIDE.md
    └── SIMPLIFICATION_PLAN.md
```

## 🔄 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                        │
│  (main.py - User Interface with Chat, Documents, Settings)  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                     FLASK BACKEND                            │
│                      (app.py)                                │
├─────────────────────────────────────────────────────────────┤
│  Authentication (JWT) │ Document Processing │ Query Handling │
└────┬──────────┬──────┴──────────┬──────────┬────────────────┘
     │          │                  │          │
     ↓          ↓                  ↓          ↓
┌────────┐ ┌─────────┐      ┌──────────┐ ┌───────────┐
│SQLite  │ │ChromaDB │      │MemoryMgr │ │ LangGraph │
│Database│ │Vector DB│      │(Encrypted│ │  Agent    │
└────────┘ └─────────┘      └──────────┘ └─────┬─────┘
                                                 │
                                                 ↓
                                          ┌──────────────┐
                                          │ Gemini LLM   │
                                          │ + Tools (9+) │
                                          └──────────────┘
```

## 📊 Data Flow

### Document Upload Flow

```
User Upload → File Validation → Save to uploads/
    ↓
Extract Text (PyPDF2/pdfminer/OCR)
    ↓
Clean & Chunk Text (500-1000 chars)
    ↓
Generate Embeddings (Sentence-BERT)
    ↓
Store in ChromaDB + Database
```

### Query Processing Flow

```
User Query → Validate & Enhance
    ↓
Load User Preferences & History
    ↓
Build Context (Role + Preferences + Documents)
    ↓
LangGraph Agent Selection
    ↓
Tool Execution (RAG Search / Case Lookup / etc)
    ↓
Gemini Generation with Context
    ↓
Save to Database → Return Response
```

---

# Memory System Documentation

## Overview

The memory system provides persistent storage for user preferences and chat history using SQLite database and encrypted preference management.

## Database Models

### Query Model

Stores all user queries and responses:

```python
class Query(Base):
    __tablename__ = 'queries'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text)
    context = Column(Text)  # JSON context used
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="queries")
```

### Memory Model

Stores encrypted user preferences:

```python
class Memory(Base):
    __tablename__ = 'memories'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text)  # Encrypted with Fernet
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="memories")
```

## Memory Manager

### Key Methods

```python
class MemoryManager:
    def store_memory(self, user_id: int, key: str, value: str):
        """Encrypts and stores a user preference"""

    def retrieve_memory(self, user_id: int, key: str) -> Optional[str]:
        """Decrypts and retrieves a user preference"""

    def get_all_memories(self, user_id: int) -> Dict[str, str]:
        """Returns all user preferences as dictionary"""

    def build_user_context(self, user_id: int, role: str) -> str:
        """Builds context string for AI prompts"""
```

### Security Features

- **Fernet Encryption** - Symmetric encryption for all stored values
- **Automatic Encryption/Decryption** - Transparent to application code
- **Key Management** - Uses environment variable `ENCRYPTION_KEY`
- **Temporary Keys** - Generates session keys if none configured

## Implementation Flows

### 1. Login Flow

```
User Login (Streamlit)
    ↓
POST /api/auth/login (Flask)
    ↓
Validate Credentials
    ↓
Generate JWT Token
    ↓
GET /api/user/{id}/history
    ↓
Load Chat History from Database
    ↓
Load Preferences from Memory Table
    ↓
Return to Frontend
    ↓
Populate Session State
```

### 2. Query Flow

```
User Asks Question
    ↓
Load User Preferences from Session
    ↓
POST /api/query or /api/agent/query
    ↓
Backend Loads Memory Context
    ↓
Build Enhanced Prompt with Context
    ↓
LLM Generation
    ↓
Save Query + Response to Database
    ↓
Return Response
```

### 3. Preferences Update Flow

```
User Changes Settings
    ↓
POST /api/user/preferences
    ↓
Validate New Preferences
    ↓
Encrypt Values (MemoryManager)
    ↓
Store in Memory Table
    ↓
Return Success
    ↓
Update Session State
```

### 4. Agent Query Flow (with Tools)

```
User Query → Validate
    ↓
Load User Context (Preferences + History)
    ↓
LangGraph Agent Initialization
    ↓
Tool Selection (RAG / Case Lookup / etc)
    ↓
Execute Tools with Context
    ↓
Aggregate Results
    ↓
Gemini Generation
    ↓
Save to Database
    ↓
Return with Tool Attribution
```

## Supported Preferences

Users can customize:

- **Practice Area** - Criminal, Civil, Corporate, etc.
- **Response Style** - Detailed, Concise, Conversational
- **Citation Format** - Bluebook, ALWD, Chicago
- **Language** - English, Hindi, etc.
- **Notification Settings** - Email, SMS preferences

## API Endpoints

### Get User History

```
GET /api/user/{user_id}/history
Authorization: Bearer <token>

Response:
{
  "chat_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "agent_history": [...],
  "preferences": {
    "practice_area": "criminal",
    "response_style": "detailed",
    "citation_format": "bluebook"
  }
}
```

### Update Preferences

```
POST /api/user/preferences
Authorization: Bearer <token>

Body:
{
  "practice_area": "criminal",
  "response_style": "detailed",
  "citation_format": "bluebook",
  "language": "english"
}

Response:
{
  "message": "Preferences updated successfully",
  "preferences": {...}
}
```

### Get Preferences

```
GET /api/user/preferences
Authorization: Bearer <token>

Response:
{
  "preferences": {
    "practice_area": "criminal",
    "response_style": "detailed",
    "citation_format": "bluebook",
    "language": "english"
  }
}
```

## Configuration

### Environment Variables

```env
# Required
ENCRYPTION_KEY=your_fernet_key_here  # Generate with: Fernet.generate_key()

# Optional
CHAT_HISTORY_LIMIT=50  # Max queries to load per session
```

### Generate Encryption Key

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Add to .env as ENCRYPTION_KEY
```

## Benefits

1. **Personalization** - AI adapts to user preferences automatically
2. **Continuity** - Pick up conversations where you left off
3. **Security** - All sensitive data encrypted at rest
4. **Scalability** - Database-backed, supports millions of users
5. **Privacy** - User data isolated, no cross-user leakage

---

# Document Processing & OCR Setup

## Document Processing Flow

### Supported Formats

- **PDF** - Text-based and image-based (with OCR)
- **DOCX** - Microsoft Word documents
- **TXT** - Plain text files

### Extraction Strategy

```
Document Upload
    ↓
┌─────────────────────┐
│  File Type Check    │
└────────┬────────────┘
         │
    ┌────┴────┐
    │   PDF?  │
    └────┬────┘
         ↓ Yes
┌─────────────────────┐
│ PyPDF2 Extraction   │ ← Fast, reliable for text PDFs
└────────┬────────────┘
         │
    Success? No ↓
         │
┌─────────────────────┐
│ pdfminer Extraction │ ← Fallback for complex PDFs
└────────┬────────────┘
         │
    <50 chars? Yes ↓
         │
┌─────────────────────┐
│ Image PDF Detected  │
└────────┬────────────┘
         │
    OCR Available? Yes ↓
         │
┌─────────────────────┐
│ Tesseract OCR       │ ← Extract from scanned images
└────────┬────────────┘
         │
    Success ↓
         │
┌─────────────────────┐
│ Clean & Chunk Text  │
└────────┬────────────┘
         │
┌─────────────────────┐
│ Generate Embeddings │
└────────┬────────────┘
         │
┌─────────────────────┐
│ Store in ChromaDB   │
└─────────────────────┘
```

## OCR Setup for Image-Based PDFs

### Problem: Scanned Documents

PDFs created by scanning physical documents contain **images of text**, not actual text data. This prevents normal extraction methods from working.

**Detection Indicators:**

- PyPDF2 extracts 0 characters
- pdfminer extracts < 50 characters for multi-page documents
- File appears blank when copied to text editor

### Solution: Tesseract OCR

#### Step 1: Install Python Libraries

```bash
# Activate virtual environment
# Windows
.\env\Scripts\Activate.ps1

# Linux/Mac
source env/bin/activate

# Install OCR dependencies
pip install pdf2image pytesseract pillow
```

#### Step 2: Install Tesseract Engine

**Windows:**

1. **Download Installer**

   - Visit: https://github.com/UB-Mannheim/tesseract/wiki
   - Download latest version (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. **Run Installer**

   - Default location: `C:\Program Files\Tesseract-OCR`
   - Select "Add to PATH" during installation

3. **Verify Installation**

   ```powershell
   tesseract --version
   # Should show: tesseract 5.x.x
   ```

4. **Manual PATH Configuration** (if needed)

   ```powershell
   # Temporary (current session)
   $env:Path += ";C:\Program Files\Tesseract-OCR"

   # Permanent (requires admin PowerShell)
   [Environment]::SetEnvironmentVariable(
       "Path",
       $env:Path + ";C:\Program Files\Tesseract-OCR",
       "Machine"
   )
   ```

**Linux:**

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Mac:**

```bash
brew install tesseract
```

#### Step 3: Configure pytesseract (Windows only, if needed)

If Tesseract is in a non-standard location:

```python
# In config.py or at app startup
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

#### Step 4: Test OCR

```bash
# Test extraction on sample PDF
python test_pdf_extraction_enhanced.py uploads\SECTION_226.pdf
```

**Expected Output:**

```
==================================================
ENHANCED PDF EXTRACTION TEST
==================================================

📄 Testing file: uploads\SECTION_226.pdf
📊 File size: 245678 bytes

✅ OCR libraries available (pdf2image, pytesseract)
✅ Tesseract OCR engine installed (version 5.3.3)

--------------------------------------------------
EXTRACTION PROCESS:
--------------------------------------------------

Attempting PyPDF2 extraction...
PDF has 1 pages
Page 1: 0 characters extracted
⚠️  PDF appears to be image-based (0 chars for 1 pages)

🔍 Attempting OCR extraction (image-based PDF detected)...
Converting PDF to images...
Processing 1 pages with OCR...
OCR processing page 1/1...
  Page 1: 1234 characters extracted

==================================================
✅ EXTRACTION SUCCESSFUL
==================================================

📊 Statistics:
   - Characters: 1,234
   - Words: 189
   - Chunks: 2

📝 Text Preview (first 500 characters):
--------------------------------------------------
SECTION 226 OF INDIAN PENAL CODE
...
```

### OCR Performance

**Extraction Times (approximate):**

- Text-based PDF (1 page): < 1 second
- Image-based PDF with OCR (1 page): 3-5 seconds
- Image-based PDF with OCR (10 pages): 30-50 seconds

**Tips for Faster OCR:**

1. Use high-quality scans (300+ DPI)
2. Ensure pages are properly aligned
3. Process in batches during off-hours
4. Consider cloud OCR services for large volumes

### Alternative Approaches

If OCR is too slow or unavailable:

#### Option 1: Convert PDF to Text-Based

**Using Adobe Acrobat Pro:**

1. Open PDF in Acrobat
2. Tools → Recognize Text → In This File
3. Save as new PDF
4. Upload the new version

**Using Online Converters:**

- ilovepdf.com - Free PDF OCR
- smallpdf.com - OCR + conversion
- onlineocr.net - Direct text extraction

#### Option 2: Upload as Text File

1. Copy text from PDF manually
2. Save as `.txt` file
3. Upload `.txt` instead of PDF
4. Instant processing (no OCR needed)

#### Option 3: Use ocrmypdf CLI

```bash
# Install
pip install ocrmypdf

# Convert PDF with OCR
ocrmypdf input.pdf output.pdf

# Upload output.pdf (now text-based)
```

### Troubleshooting

#### Error: "Tesseract not found"

**Solution:**

```powershell
# Check if installed
tesseract --version

# Add to PATH manually
$env:Path += ";C:\Program Files\Tesseract-OCR"

# Restart terminal
```

#### Error: "DLL load failed" (Windows)

**Solution:**

1. Install Visual C++ Redistributable
2. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
3. Restart computer

#### OCR Produces Gibberish

**Possible Causes:**

- Poor scan quality
- Wrong language setting
- Corrupted PDF

**Solutions:**

```python
# Set language explicitly
pytesseract.image_to_string(image, lang='eng')

# For Hindi/multilingual
pytesseract.image_to_string(image, lang='eng+hin')

# Improve image preprocessing
from PIL import ImageEnhance
enhancer = ImageEnhance.Contrast(image)
image = enhancer.enhance(2.0)
```

### Verification Commands

```bash
# Check Python libraries
python -c "import pdf2image, pytesseract; print('✅ OCR libs installed')"

# Check Tesseract
tesseract --version

# Test end-to-end
python test_pdf_extraction_enhanced.py uploads\test.pdf
```

---

# API Reference

## Authentication Endpoints

### Register User

```
POST /api/auth/register

Body:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "role": "lawyer"  // lawyer, student, or public
}

Response: 200 OK
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "role": "lawyer"
  }
}
```

### Login

```
POST /api/auth/login

Body:
{
  "username": "john_doe",
  "password": "secure_password"
}

Response: 200 OK
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "lawyer"
  }
}
```

## Document Endpoints

### Upload Document

```
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

Body:
- file: [PDF/DOCX/TXT file]

Response: 200 OK
{
  "message": "Document uploaded and processed successfully",
  "document_id": "uuid-here",
  "metadata": {
    "char_count": 5000,
    "word_count": 850,
    "file_type": "pdf"
  },
  "chunks_count": 5
}
```

### List Documents

```
GET /api/documents
Authorization: Bearer <token>

Response: 200 OK
{
  "documents": [
    {
      "doc_id": "uuid-1",
      "filename": "contract.pdf",
      "file_type": "pdf",
      "uploaded_at": "2025-11-17T10:30:00",
      "processed": "completed"
    }
  ]
}
```

### Analyze Document

```
POST /api/documents/{doc_id}/analyze
Authorization: Bearer <token>

Body:
{
  "query": "Summarize this document",
  "type": "comprehensive"  // comprehensive, summary, specific, qa
}

Response: 200 OK
{
  "doc_id": "uuid-here",
  "analysis": "...",
  "key_elements": {...},
  "metadata": {...}
}
```

### Delete Document

```
DELETE /api/documents/{doc_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "message": "Document deleted successfully"
}
```

## Query Endpoints

### Basic Query

```
POST /api/query
Authorization: Bearer <token>

Body:
{
  "query": "What is Section 420 IPC?",
  "mode": "short"  // short or detailed
}

Response: 200 OK
{
  "query": "What is Section 420 IPC?",
  "response": "Section 420 of IPC deals with cheating...",
  "role": "lawyer",
  "timestamp": "2025-11-17T10:30:00"
}
```

### Agent Query (with Tools)

```
POST /api/agent/query
Authorization: Bearer <token>

Body:
{
  "query": "Find cases related to Section 420",
  "max_iterations": 10
}

Response: 200 OK
{
  "query": "Find cases related to Section 420",
  "answer": "...",
  "tools_used": [
    {"tool": "search_legal_cases", "result": "..."}
  ],
  "iterations": 3,
  "sources": [...],
  "confidence": 0.92
}
```

## RAG Endpoints

### Search Documents

```
POST /api/rag/search
Authorization: Bearer <token>

Body:
{
  "query": "contract termination clauses",
  "top_k": 5
}

Response: 200 OK
{
  "query": "contract termination clauses",
  "results": [
    {
      "chunk_id": "uuid_0",
      "doc_id": "uuid",
      "text": "...",
      "similarity": 0.89,
      "doc_title": "contract.pdf"
    }
  ]
}
```

### Query Document

```
POST /api/rag/documents/{doc_id}/query
Authorization: Bearer <token>

Body:
{
  "question": "What are the payment terms?"
}

Response: 200 OK
{
  "doc_id": "uuid",
  "question": "What are the payment terms?",
  "answer": "The payment terms are...",
  "sources": [...]
}
```

### Compare Documents

```
POST /api/rag/documents/compare
Authorization: Bearer <token>

Body:
{
  "doc_id1": "uuid-1",
  "doc_id2": "uuid-2"
}

Response: 200 OK
{
  "similarity": 0.75,
  "common_topics": [...],
  "unique_to_doc1": [...],
  "unique_to_doc2": [...]
}
```

## User Endpoints

### Get User History

```
GET /api/user/{user_id}/history
Authorization: Bearer <token>

Response: 200 OK
{
  "chat_history": [...],
  "agent_history": [...],
  "preferences": {...}
}
```

### Update Preferences

```
POST /api/user/preferences
Authorization: Bearer <token>

Body:
{
  "practice_area": "criminal",
  "response_style": "detailed",
  "citation_format": "bluebook"
}

Response: 200 OK
{
  "message": "Preferences updated successfully"
}
```

### Get Preferences

```
GET /api/user/preferences
Authorization: Bearer <token>

Response: 200 OK
{
  "preferences": {
    "practice_area": "criminal",
    "response_style": "detailed"
  }
}
```

## System Endpoints

### Status Check

```
GET /api/status

Response: 200 OK
{
  "status": "running",
  "version": "2.0.0",
  "services": {
    "orchestrator": true,
    "reasoning_engine": true,
    "rag_tool": true
  },
  "database": "connected"
}
```

---

# Simplification Plan

## Current Problems

### 1. Too Many Similar Features

- Multiple RAG implementations (ChromaDB + LangChain + custom routes)
- Duplicate document processing flows
- Overlapping query endpoints (`/api/query` and `/api/agent/query`)
- Multiple storage systems (document_storage/ + chromadb_storage/ + database)

### 2. Confusing Architecture

- Too many modules doing similar things
- Unclear separation between features
- Multiple ways to do the same thing
- Orphaned/unused code

### 3. Complex User Experience

- Too many pages in frontend (7+ navigation options)
- Unclear difference between "Legal Assistant" and "Agent Query"
- Confusing "Document RAG" page separate from "Document Analysis"

### 4. Technical Debt

- Unused imports and modules
- Multiple test files with overlap
- Inconsistent error handling
- Mixed storage approaches

## 🚀 Simplification Strategy

### Phase 1: Consolidate Core Features (IMMEDIATE)

#### A. Merge Document Features → Single "Documents" Page

**Before:** 3 separate pages

- Document Analysis
- Document RAG
- My Documents

**After:** 1 unified "Documents" page with tabs

- Upload & Analyze
- My Documents
- Chat with Documents

#### B. Merge Chat Endpoints → Single Intelligent Query Handler

**Before:** 2 endpoints

- `/api/query` - Basic legal assistant
- `/api/agent/query` - Agent with tools

**After:** 1 smart endpoint

- `/api/chat` - Auto-detects if documents/tools needed

**Logic:**

```python
@app.route('/api/chat', methods=['POST'])
def smart_chat():
    # 1. Analyze query complexity
    # 2. Check if user has documents
    # 3. Auto-route to simple or agent mode
    # 4. Return unified response
```

#### C. Consolidate Storage → Single Source of Truth

**Before:**

- Database (luminary.db) - metadata
- ChromaDB (chromadb_storage/) - vectors
- Files (document_storage/) - unused!
- Files (uploads/) - actual files

**After:**

- Database - all metadata + chat history
- ChromaDB - all vectors (documents + chunks)
- uploads/ - actual files only

**Remove:**

- `document_storage/` folder (unused)
- Legacy RAG implementation files

### Phase 2: Streamline Frontend (1 DAY)

#### Navigation Simplification

**Before:** 8 navigation items

```
- Legal Assistant
- Legal Research
- Document Analysis
- Document RAG
- Agent Query
- My Documents
- Settings
- Logout
```

**After:** 4 navigation items

```
- 💬 Chat (merged Legal Assistant + Agent)
- 📄 Documents (merged all document features)
- ⚙️ Settings
- 🚪 Logout
```

#### Page Consolidation

**Merge into "Chat" page:**

- Legal Assistant → Default view
- Agent Query → Advanced mode (toggle button)
- Auto-detection of tool needs

**Merge into "Documents" page:**

- Upload & Analyze (tab 1)
- My Documents (tab 2)
- Document Q&A (tab 3)

### Phase 3: Code Cleanup (2 DAYS)

#### Remove Redundant Files

**Delete:**

- `modules/document_rag_tool.py` (legacy RAG - migrated to ChromaDB)
- `test_agent_tools.py`, `test_agent.py` (covered by test_suite.py)
- `test_tools_check.py` (redundant)
- `document_storage/` folder

**Keep:**

- `modules/document_rag_chromadb.py` (primary RAG)
- `modules/document_rag_langchain.py` (tool wrappers)
- `test_suite.py` (comprehensive)
- `test_pdf_extraction.py` (specific)

#### Consolidate Utilities

**Before:** Scattered helper functions

**After:** Organized in `utils/`

- `utils/validators.py` - Input validation
- `utils/formatters.py` - Response formatting
- `utils/helpers.py` - General utilities

### Phase 4: Optimize Performance (ONGOING)

#### Caching Strategy

- Cache ChromaDB queries (30 min TTL)
- Cache user preferences (session lifetime)
- Cache document metadata (until update)

#### Database Optimization

- Add indexes on frequently queried fields
- Implement connection pooling
- Clean up old chat history (> 90 days)

## Success Metrics

### Before vs After

| Metric           | Before | After | Improvement |
| ---------------- | ------ | ----- | ----------- |
| Navigation Items | 8      | 4     | -50%        |
| API Endpoints    | 15+    | 10    | -33%        |
| Core Modules     | 12     | 8     | -33%        |
| Test Files       | 6      | 3     | -50%        |
| Lines of Code    | ~8000  | ~5500 | -31%        |
| Storage Folders  | 4      | 2     | -50%        |
| User Confusion   | High   | Low   | ✅          |

### User Experience Improvements

**Navigation Clarity:**

- From: "Should I use Document Analysis or Document RAG?"
- To: "Everything document-related is in Documents page"

**Query Simplicity:**

- From: "Do I need Agent Query for this?"
- To: "Just ask - the system figures it out"

**Storage Understanding:**

- From: "Where is my document stored?"
- To: "All documents in one place with clear metadata"

## Quick Wins (3 HOURS)

Priority actions for immediate 50% complexity reduction:

### 1. Merge Document Pages (1 hour)

```python
# main.py - Add tabbed interface
if page == "Documents":
    tab1, tab2, tab3 = st.tabs(["Upload & Analyze", "My Documents", "Chat with Docs"])
    # Consolidate all document features
```

### 2. Delete Unused Files (30 min)

```bash
rm -rf document_storage/
rm modules/document_rag_tool.py
rm test_agent.py test_agent_tools.py test_tools_check.py
```

### 3. Simplify Navigation (30 min)

```python
# Reduce from 8 to 4 items
pages = ["💬 Chat", "📄 Documents", "⚙️ Settings", "🚪 Logout"]
```

### 4. Consolidate Endpoints (1 hour)

```python
# Create smart /api/chat endpoint
# Deprecate separate /api/query and /api/agent/query
```

## Migration Path

For existing users:

1. **Data Migration** - None needed (database schema unchanged)
2. **API Compatibility** - Old endpoints still work (marked deprecated)
3. **Frontend Update** - New navigation + merged pages
4. **Documentation** - Update user guides

---

# Troubleshooting

## Common Issues

### 1. "GOOGLE_API_KEY not configured"

**Problem:** Gemini API key missing or invalid

**Solution:**

```bash
# Add to .env file
GOOGLE_API_KEY=your_actual_api_key_here

# Verify
python -c "from config import Config; print(Config.GOOGLE_API_KEY[:10])"
```

### 2. "Could not extract text from PDF"

**Problem:** PDF is image-based (scanned)

**Solutions:**

1. Install OCR dependencies (see OCR Setup section)
2. Convert PDF to text-based format
3. Upload as `.txt` file instead

### 3. "ChromaDB collection not found"

**Problem:** Vector database not initialized

**Solution:**

```python
# Reinitialize ChromaDB
from modules.document_rag_chromadb import ChromaDBRAGTool
rag = ChromaDBRAGTool(storage_path="chromadb_storage")
```

### 4. "JWT token expired"

**Problem:** Authentication token expired (24h default)

**Solution:**

- Log out and log back in
- Token automatically refreshed

### 5. "Database locked" (SQLite)

**Problem:** Concurrent access conflict

**Solutions:**

```python
# Use connection pooling
from sqlalchemy.pool import StaticPool

engine = create_engine(
    'sqlite:///luminary.db',
    poolclass=StaticPool,
    connect_args={'check_same_thread': False}
)
```

### 6. Slow Document Processing

**Causes:**

- Large files (>10MB)
- Image-based PDFs requiring OCR
- Complex document structure

**Solutions:**

- Split large documents
- Use text-based PDFs when possible
- Process in background (async)

### 7. Memory/Preferences Not Saving

**Problem:** Encryption key missing or invalid

**Solution:**

```python
# Generate new key
from cryptography.fernet import Fernet
key = Fernet.generate_key()

# Add to .env
ENCRYPTION_KEY=<generated_key>
```

---

## 📄 Disclaimer

⚠️ **Important Legal Notice:**

LuminaryAI is an AI-powered research assistant and **should NOT be considered a substitute for professional legal advice**. While we strive for accuracy:

- AI-generated responses may contain errors or omissions
- Laws change frequently; always verify with current statutes
- Consult qualified legal professionals for specific legal matters
- Do not rely solely on AI for legal decisions

**Use responsibly and verify all information independently.**

---

## 📞 Support & Contact

- **GitHub Issues:** https://github.com/HitkarMiglani/legal_Test/issues
- **Email:** support@luminaryai.com
- **Documentation:** This file (COMPLETE_DOCUMENTATION.md)

---

## 📜 License

This project is licensed under the MIT License.

---

**Last Updated:** November 17, 2025  
**Version:** 2.0.0  
**Author:** HitkarMiglani
