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

## 🧩 Installation

### Quick Setup (Recommended)

```powershell
# Windows PowerShell
.\setup.ps1
```

Or manually:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "from models import init_db; init_db()"
```

### Configure API Keys

1. Copy `.env.example` to `.env`
2. Add your Google Gemini API key: https://makersuite.google.com/app/apikey
3. Generate Fernet key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

### Verify Setup

```powershell
python test_setup.py
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

## 🎯 Key Features & Guides

- **[Query Reiteration & Role Context](QUERY_REITERATION.md)** - Automatic query enhancement with role-based responses
- **[Query Validation & Semantic Answers](QUERY_VALIDATION.md)** - Smart query validation with short/detailed response modes
- **[Setup Guide](SETUP.md)** - Detailed installation instructions
- **[Quick Start](QUICKSTART.md)** - Get started in 5 minutes
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

## 📁 Project Structure

```
LuminaryAI/
├── app.py                      # Flask backend application
├── main.py                     # Streamlit frontend
├── config.py                   # Configuration management
├── models.py                   # Database models (SQLAlchemy)
├── utils.py                    # Utility functions
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
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project structure and file organization
- **[DOCUMENT_RAG_TOOL.md](DOCUMENT_RAG_TOOL.md)** - RAG pipeline technical docs
- **[LANGCHAIN_INTEGRATION.md](LANGCHAIN_INTEGRATION.md)** - LangChain agent guide
- **[SETUP.md](SETUP.md)** - Detailed setup instructions

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
