# ⚖️ LuminaryAI — Agentic Legal Intelligence Assistant for Indian Law

> "Making Indian law understandable, accessible, and intelligent — for everyone."

## 🧩 Overview

LuminaryAI is an **intelligent, document-aware legal assistant** with autonomous capabilities, designed to analyze legal documents, interpret Indian laws, and provide tailored legal insights for practising lawyers, law students, and the general public.

Built using **LangChain, Gemini LLM, RAG (Retrieval-Augmented Generation), and Python**, LuminaryAI offers:

- 🤖 **Autonomous document management** via intelligent agents
- 📚 **Persistent knowledge base** with semantic search
- 🎯 **Context-aware legal advice** based on your documents
- ⚡ **Multi-document operations** in single queries
- 🔍 **Source citations** with confidence scores

All through a Streamlit-based frontend and Flask-powered backend with **9 intelligent tools** for document operations.

## 🌟 Key Features

### 🆕 **Document Management & RAG**

- **🤖 Autonomous Agent** - LLM autonomously manages documents using 9 intelligent tools
- **📚 Document RAG Pipeline** - Semantic search with Gemini embeddings (768-dim vectors)
- **🔍 Intelligent Search** - Find relevant clauses across all documents instantly
- **💬 Document Q&A** - Ask questions about specific documents
- **📊 Multi-Doc Analysis** - Compare documents, extract insights, identify risks
- **📁 Persistent Knowledge Base** - Store and retrieve documents with metadata
- **🎯 Source Citations** - All answers include source documents with similarity scores

### ⚡ **Core AI Features**

- **Agentic Legal Intelligence** (LangChain + Gemini + 9 Tools)
- **Smart Query Enhancement** - Automatic query reiteration for clarity (score < 8)
- **Role-Based Responses** - Tailored answers for Lawyers/Students/Public
- **Query Validation & Semantic Answers** - Intelligent query analysis with short/detailed response modes
- **Document Analysis** (PDF/DOCX/TXT)
- **Real-Time Legal Intelligence** (Indian Kanoon API)
- **Semantic Search & Matching** (LegalBERT + Embeddings)
- **Personalized Memory** (Secure Storage)
- **Mobile-First Interface** (Streamlit)
- **Cloud/Local Storage Support** (Firebase, AWS, SQLite)

## 🧱 System Architecture

[Architecture Diagram Section Omitted for Brevity]

## 🧰 Technology Stack

| Layer               | Technology                       |
| ------------------- | -------------------------------- |
| Frontend            | Streamlit                        |
| Backend             | Flask                            |
| AI Layer            | LangChain, Gemini LLM, LegalBERT |
| Embeddings          | text-embedding-004 / LegalBERT   |
| Storage             | Firebase / AWS S3 / SQLite       |
| Auth                | JWT, bcrypt                      |
| Document Processing | pdfminer, docx2txt               |
| APIs                | Indian Kanoon, OpenLaw           |
| Security            | Fernet Encryption                |

## 🧮 Core Modules

- User Authentication
- Document Processor
- Embedding Generator
- LangChain Orchestrator
- Gemini Reasoning Engine
- Legal Retriever
- Memory Manager
- UI Display Manager

## 🧩 Installation & Setup

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Virtual environment (recommended)
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Quick Setup (Recommended)

```powershell
# Windows PowerShell
.\setup.ps1
```

### Manual Setup

#### 1. Create Virtual Environment

```powershell
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

#### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

#### 3. Configure Environment

```powershell
# Copy environment template
cp env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```env
GOOGLE_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=generate-random-string
JWT_SECRET_KEY=generate-random-string
FERNET_KEY=generate-fernet-key
```

**Generate Keys:**
```bash
# Generate Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate secret keys (use openssl or random string)
openssl rand -hex 32
```

#### 4. Initialize Database

```powershell
python -c "from models import init_db; init_db()"
```

### Verify Setup

```powershell
python test_suite.py
```

## ⚙️ Run

**Terminal 1 - Backend:**

```powershell
python app.py
```

**Terminal 2 - Frontend:**

```powershell
streamlit run main.py
```

**Access:**

- Frontend: <http://localhost:8501>
- Backend API: <http://localhost:5000>

## 🧪 Test

```powershell
# Run comprehensive test suite
python test_suite.py

# Run specific tests
python test_suite.py --test rag
python test_suite.py --test langchain
python test_suite.py --test app
```

## 🚀 Quick Deployment (Docker)

```bash
# Copy environment file
cp env.example .env

# Edit .env and add API keys
nano .env

# Start all services
docker-compose up -d

# Access
# Frontend: http://localhost:8501
# Backend: http://localhost:5000
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

## 📁 Project Structure

```
LuminaryAI/
├── app.py                      # Flask backend application
├── main.py                     # Streamlit frontend
├── config.py                   # Configuration management
├── models.py                   # Database models (SQLAlchemy)
├── utils/                      # Utility modules (logger, exceptions, middleware)
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── setup.ps1                  # Windows setup script
├── setup.sh                   # Linux/Mac setup script
├── test_setup.py              # Setup verification script
├── SETUP.md                   # Detailed setup guide
├── QUICKSTART.md              # Quick start guide
├── modules/                   # Core modules
│   ├── __init__.py
│   ├── auth.py               # JWT authentication
│   ├── document_processor.py # PDF/DOCX/TXT processing
│   ├── embeddings.py         # Gemini embeddings
│   ├── legal_retriever.py    # Indian Kanoon integration
│   ├── memory_manager.py     # User memory/preferences
│   ├── orchestrator.py       # LangChain orchestration
│   └── reasoning_engine.py   # Gemini reasoning
└── uploads/                   # Document storage (auto-created)
```

## 📚 Documentation

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete API reference, usage examples, architecture
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide (Docker, manual, scaling)
- **[DOCUMENT_RAG_TOOL.md](DOCUMENT_RAG_TOOL.md)** - RAG pipeline technical documentation
- **[LANGCHAIN_INTEGRATION.md](LANGCHAIN_INTEGRATION.md)** - LangChain agent integration guide

## 🎯 Quick Reference

| Resource         | Command/URL                  |
| ---------------- | ---------------------------- |
| **Test Suite**   | `python test_suite.py`       |
| **API Docs**     | `GET http://localhost:5000/` |
| **Status Check** | `GET /api/status`            |
| **Agent Query**  | `POST /api/agent/query`      |

## ⚠️ Disclaimer

LuminaryAI provides AI-generated summaries of Indian laws and legal documents for educational and informational purposes only. It is not a substitute for professional legal advice.

## 📧 Contact

<support@Luminaryai.in>

---

**Version: 2.0.0** | **Status: Production Ready** ✅
