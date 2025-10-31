# 📁 LuminaryAI Project Structure

## Core Application Files

```
Agentic_Law_AI/
│
├── app.py                      # Flask backend (main application)
├── main.py                     # Streamlit frontend
├── config.py                   # Configuration management
├── models.py                   # Database models (SQLAlchemy)
├── utils.py                    # Utility functions
│
├── modules/                    # Core modules
│   ├── __init__.py
│   ├── auth.py                # Authentication (JWT, bcrypt)
│   ├── document_processor.py  # PDF/DOCX/TXT processing
│   ├── embeddings.py          # Embedding generation
│   ├── legal_retriever.py     # Indian Kanoon API integration
│   ├── memory_manager.py      # User context management
│   ├── orchestrator.py        # LangChain orchestration
│   ├── reasoning_engine.py    # Gemini document analysis
│   ├── document_rag_tool.py   # RAG pipeline (9 methods)
│   ├── document_rag_langchain.py  # LangChain tools (9 tools)
│   └── document_rag_routes.py     # Flask RAG API routes
│
├── test_suite.py              # Comprehensive test suite
│
├── .env                       # Environment variables (API keys)
├── .env.example              # Example environment file
├── requirements.txt          # Python dependencies
│
├── setup.ps1                 # Windows setup script
├── setup.sh                  # Linux/Mac setup script
├── run.ps1                   # Windows run script
├── run.sh                    # Linux/Mac run script
│
├── luminary.db               # SQLite database
├── uploads/                  # Uploaded files
└── __pycache__/              # Python cache
```

## Documentation

```
├── README.md                 # Project overview & quick start
├── DOCUMENTATION.md          # Complete documentation (API, usage, etc.)
├── DOCUMENT_RAG_TOOL.md      # RAG tool technical guide
├── LANGCHAIN_INTEGRATION.md  # LangChain agent guide
└── SETUP.md                  # Detailed setup instructions
```

## Virtual Environment

```
env/                          # Python virtual environment
├── Scripts/                  # Windows executables
│   ├── activate
│   ├── activate.ps1
│   ├── python.exe
│   └── pip.exe
├── Lib/                      # Python libraries
│   └── site-packages/        # Installed packages
└── pyvenv.cfg               # Virtual env configuration
```

---

## Module Descriptions

### Core Application

**`app.py`** - Flask Backend

- Main Flask application
- 16+ API endpoints
- Authentication middleware
- RAG blueprint registration
- Agent endpoint for autonomous operations

**`main.py`** - Streamlit Frontend

- User interface
- Chat interface
- Document upload
- Query submission

**`config.py`** - Configuration

- Environment variable management
- API key configuration
- Database settings
- LLM parameters

**`models.py`** - Database Models

- User model (authentication)
- Document model (uploaded files)
- Query model (conversation history)
- SQLAlchemy ORM

### Core Modules

**`auth.py`** - Authentication

- JWT token generation/validation
- Password hashing (bcrypt)
- Token-required decorator
- User session management

**`document_processor.py`** - Document Processing

- PDF text extraction (pdfminer)
- DOCX text extraction (docx2txt)
- TXT file reading
- File validation

**`embeddings.py`** - Embedding Generation

- Gemini embedding-001 model
- Vector generation for search
- Batch embedding support

**`legal_retriever.py`** - Legal Research

- Indian Kanoon API integration
- Case law search
- Citation extraction

**`memory_manager.py`** - Context Management

- User conversation history
- Context building
- Personalized responses

**`orchestrator.py`** - LangChain Orchestration

- Chain creation
- Prompt templates
- Role-based prompts
- Memory integration

**`reasoning_engine.py`** - Gemini Analysis

- Document analysis (15+ methods)
- Query validation
- Legal advice generation
- Entity extraction
- Risk identification
- Document comparison

**`document_rag_tool.py`** - RAG Pipeline

- 9 core methods:
  1. add_document
  2. search_documents
  3. query_document
  4. list_documents
  5. get_document
  6. delete_document
  7. compare_documents
  8. semantic_search_all
  9. get_statistics
- Chunking strategy
- Embedding generation
- Cosine similarity search
- JSON-based storage

**`document_rag_langchain.py`** - LangChain Tools

- 9 LangChain BaseTool wrappers
- Pydantic input schemas
- Agent-ready tools
- Tool factory function

**`document_rag_routes.py`** - RAG API

- 9 Flask endpoints
- Token authentication
- Error handling
- Response formatting

### Testing

**`test_suite.py`** - Comprehensive Tests

- 6 test categories:
  1. Module imports
  2. Gemini reasoning engine
  3. Document RAG tool
  4. LangChain tools
  5. Flask app integration
  6. Direct tool usage
- Command-line options
- Detailed reporting

---

## Data Flow

### 1. Document Upload Flow

```
User Upload (Frontend)
    ↓
app.py (/api/documents/upload)
    ↓
DocumentProcessor.extract_text()
    ↓
Save to database (models.py)
    ↓
Optionally add to RAG (DocumentRAGTool.add_document())
    ↓
Chunking + Embedding + Storage
```

### 2. Query Flow (Document-Aware)

```
User Query (Frontend)
    ↓
app.py (/api/query)
    ↓
GeminiReasoningEngine.validate_query()
    ↓
DocumentRAGTool.semantic_search_all() [NEW!]
    ↓
LegalRetriever.search_cases()
    ↓
MemoryManager.build_user_context()
    ↓
GeminiReasoningEngine.generate_legal_advice()
    ↓
Response with documents + cases
```

### 3. Agent Flow (Autonomous)

```
User Query (Frontend)
    ↓
app.py (/api/agent/query)
    ↓
LangChain Agent (create_react_agent)
    ↓
Agent Reasoning Loop:
  │ → Select Tool
  │ → Execute Tool
  │ → Observe Result
  │ → Decide: Continue or Finish?
  └── Loop until answer
    ↓
Final Answer with Sources
```

---

## API Endpoint Map

### Authentication

- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - User login

### Documents

- POST `/api/documents/upload` - Upload document
- GET `/api/documents` - List user's documents
- POST `/api/documents/analyze` - Analyze document

### Queries

- POST `/api/query` - Document-aware query (enhanced)
- POST `/api/agent/query` - Autonomous agent query (NEW!)

### RAG Operations

- POST `/api/rag/documents` - Add to knowledge base
- GET `/api/rag/documents` - List all
- GET `/api/rag/documents/{id}` - Get specific
- DELETE `/api/rag/documents/{id}` - Delete
- POST `/api/rag/search` - Semantic search
- POST `/api/rag/documents/{id}/query` - Document Q&A
- POST `/api/rag/documents/compare` - Compare docs
- POST `/api/rag/search/semantic` - Advanced search
- GET `/api/rag/statistics` - Statistics

### Research

- GET `/api/research/cases` - Search case law

### Health

- GET `/api/health` - Health check
- GET `/api/status` - Detailed status
- GET `/` - API documentation

---

## Storage Structure

### Database (luminary.db)

```sql
users
├── id (PK)
├── username
├── email
├── password_hash
├── role (lawyer/student/public)
└── created_at

documents
├── id (PK)
├── user_id (FK)
├── filename
├── file_path
├── content
└── uploaded_at

queries
├── id (PK)
├── user_id (FK)
├── query_text
├── response_text
└── created_at
```

### RAG Storage (document_storage/)

```
document_storage/
├── index.json              # Master index
├── documents/              # Full documents
│   ├── abc123.txt
│   └── def456.txt
└── chunks/                 # Chunks with embeddings
    ├── abc123_0.json      # {chunk_id, doc_id, text, embedding, length}
    ├── abc123_1.json
    └── def456_0.json
```

---

## Configuration Files

### `.env` - Environment Variables

```env
GOOGLE_API_KEY=your_api_key_here
LLM_MODEL=gemini-pro
TEMPERATURE=0.7
MAX_TOKENS=2048
FLASK_PORT=5000
DATABASE_URL=sqlite:///luminary.db
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
UPLOAD_FOLDER=uploads
```

### `requirements.txt` - Dependencies

```txt
flask
flask-cors
streamlit
google-generativeai
langchain
langchain-google-genai
pydantic
sqlalchemy
bcrypt
pyjwt
pdfminer.six
python-docx
numpy
requests
```

---

## Development Workflow

### 1. Setup

```bash
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure

```bash
# Create .env file
echo "GOOGLE_API_KEY=your_key" > .env
```

### 3. Test

```bash
python test_suite.py
```

### 4. Run

```bash
# Terminal 1
python app.py

# Terminal 2
streamlit run main.py
```

### 5. Develop

- Edit modules in `modules/`
- Test with `test_suite.py`
- Check endpoints with curl/Postman

---

## Key Design Decisions

### Why Flask + Streamlit?

- **Flask**: RESTful API, easy to deploy, lightweight
- **Streamlit**: Rapid UI development, perfect for demos

### Why File-Based RAG Storage?

- **Simplicity**: No external dependencies
- **Portability**: Easy to backup/move
- **Transparency**: Human-readable JSON
- **Scale**: Good for <100k documents
- **Upgrade Path**: Easy to migrate to vector DB later

### Why Gemini?

- **Quality**: Excellent legal reasoning
- **Embeddings**: Built-in embedding-001 model
- **Cost**: Competitive pricing
- **API**: Simple, well-documented

### Why LangChain for Agent?

- **Standard**: Industry-standard agent framework
- **Flexibility**: Easy to add tools
- **Debugging**: Good observability
- **Community**: Large ecosystem

---

## Future Enhancements

### Planned

- [ ] Vector database (Pinecone/Weaviate) for scale
- [ ] Document versioning
- [ ] Access control per document
- [ ] Admin dashboard
- [ ] Batch operations
- [ ] Caching layer
- [ ] Analytics dashboard
- [ ] Export functionality

### Possible

- [ ] Multi-language support
- [ ] Voice interface
- [ ] Mobile app
- [ ] Slack/Teams integration
- [ ] PDF generation
- [ ] Email notifications

---

## Performance Considerations

### Bottlenecks

1. **Embedding generation**: ~200ms per chunk (Gemini API)
2. **Search**: Linear O(n) over all chunks
3. **Storage**: File I/O for each chunk

### Optimizations

- **Batch embeddings**: Process multiple chunks together
- **Caching**: Cache frequent queries
- **Async**: Use async/await for I/O
- **Vector DB**: Use for large-scale deployments
- **CDN**: For static assets in production

---

## Security Considerations

### Authentication

- JWT tokens with expiration
- Password hashing with bcrypt
- Token refresh mechanism

### Data Protection

- User-specific document isolation
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- API rate limiting (recommended)

### Production Checklist

- [ ] HTTPS/TLS encryption
- [ ] Environment variables (not hardcoded)
- [ ] Secure secret keys
- [ ] Regular security updates
- [ ] Backup strategy
- [ ] Logging and monitoring
- [ ] Input validation
- [ ] Error message sanitization

---

## Monitoring & Logging

### Recommended Tools

- **Application**: Flask-Logging
- **Performance**: Flask-Profiler
- **Errors**: Sentry
- **Analytics**: Mixpanel/Google Analytics
- **Infrastructure**: Prometheus + Grafana

### Key Metrics

- API response times
- Document processing times
- RAG search performance
- Agent tool usage
- Error rates
- User activity

---

_Last Updated: October 30, 2025_
_Version: 2.0.0_
