"""
Flask Backend for LuminaryAI
"""
import os
import warnings
from datetime import datetime

# Suppress gRPC warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
warnings.filterwarnings('ignore', category=DeprecationWarning)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import config, Config
from models import init_db, get_session, User, Document, Query, UserRole
from modules.auth import auth_manager
from modules.document_processor import DocumentProcessor
from modules.legal_retriever import LegalRetriever
from modules.memory_manager import MemoryManager
from modules.orchestrator import LangChainOrchestrator
from modules.reasoning_engine import GeminiReasoningEngine
from modules.document_rag_chromadb import ChromaDBRAGTool  # NEW: ChromaDB instead of Gemini embeddings
from modules.document_rag_langchain import create_document_rag_tools
from modules.document_rag_routes import rag_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])
CORS(app)

# Initialize database
engine = init_db(app.config['DATABASE_URL'])

# Initialize modules with error handling
doc_processor = DocumentProcessor(app.config['UPLOAD_FOLDER'])
legal_retriever = LegalRetriever()
orchestrator = None
reasoning_engine = None
rag_tool = None
langchain_tools = None

# Initialize AI modules with proper error handling
try:
    if Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_gemini_api_key_here':
        orchestrator = LangChainOrchestrator()
        reasoning_engine = GeminiReasoningEngine()
        
        # Initialize Document RAG Tool with ChromaDB (no API quota limits!)
        rag_tool = ChromaDBRAGTool(storage_path="chromadb_storage", model_name="all-MiniLM-L6-v2")
        langchain_tools = create_document_rag_tools(rag_tool=rag_tool)
        
        print("✓ AI modules initialized successfully")
        print(f"✓ Document RAG Tool initialized with {len(langchain_tools)} LangChain tools")
    else:
        print("⚠ Warning: GOOGLE_API_KEY not configured. AI features will be limited.")
        print("  Please set your API key in the .env file.")
except Exception as e:
    print(f"⚠ Warning: Failed to initialize AI modules: {str(e)}")
    print("  The application will run with limited functionality.")

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register Document RAG API routes
app.register_blueprint(rag_bp)
print("✓ Document RAG API routes registered at /api/rag/*")

# ============== Authentication Routes ==============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'public')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        session = get_session(engine)
        
        # Check if user exists
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            session.close()
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        password_hash = auth_manager.hash_password(password)
        
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=UserRole[role.upper()]
        )
        
        session.add(new_user)
        session.commit()
        
        # Generate token
        token = auth_manager.generate_token(new_user.id, username, role)
        
        session.close()
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': new_user.id,
                'username': username,
                'email': email,
                'role': role
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'Missing credentials'}), 400
        
        session = get_session(engine)
        
        # Find user
        user = session.query(User).filter(User.username == username).first()
        
        if not user or not auth_manager.verify_password(password, user.password_hash):
            session.close()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        session.commit()
        
        # Generate token
        token = auth_manager.generate_token(user.id, user.username, user.role.value)
        
        session.close()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== Document Routes ==============

@app.route('/api/documents/upload', methods=['POST'])
@auth_manager.token_required
def upload_document():
    """Upload and process a legal document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not doc_processor.is_allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        file_ext = doc_processor.get_file_extension(filename)
        
        # Save file
        file_path = doc_processor.save_uploaded_file(file, filename)
        
        # Get user info
        user_id = request.current_user['user_id']
        
        # Create document record
        session = get_session(engine)
        
        new_doc = Document(
            user_id=user_id,
            filename=filename,
            file_type=file_ext,
            file_path=file_path,
            processed='processing'
        )
        
        session.add(new_doc)
        session.commit()
        doc_id = new_doc.id
        session.close()
        
        # Process document (in background in production)
        try:
            result = doc_processor.process_document(file_path, file_ext)
            
            # Update document status
            session = get_session(engine)
            doc = session.query(Document).get(doc_id)
            doc.processed = 'completed'
            session.commit()
            session.close()
            
            return jsonify({
                'message': 'Document uploaded and processed',
                'document_id': doc_id,
                'metadata': result['metadata']
            }), 200
            
        except Exception as e:
            session = get_session(engine)
            doc = session.query(Document).get(doc_id)
            doc.processed = 'failed'
            session.commit()
            session.close()
            
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<int:doc_id>/analyze', methods=['POST'])
@auth_manager.token_required
def analyze_document(doc_id):
    """Analyze a document using enhanced Gemini-only processing"""
    try:
        data = request.get_json() or {}
        query = data.get('query', None)
        analysis_type = data.get('type', 'comprehensive')  # comprehensive, summary, specific, qa
        
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        session = get_session(engine)
        
        # Get document
        doc = session.query(Document).filter_by(id=doc_id, user_id=user_id).first()
        
        if not doc:
            session.close()
            return jsonify({'error': 'Document not found'}), 404
        
        # Check if Gemini reasoning engine is available
        if not reasoning_engine:
            session.close()
            return jsonify({
                'error': 'AI service not available. Please configure GOOGLE_API_KEY in .env file and restart the server.'
            }), 503
        
        # Process document to extract text
        result = doc_processor.process_document(doc.file_path, doc.file_type)
        document_text = result['text']
        document_metadata = result['metadata']
        
        # Perform enhanced Gemini-based analysis
        try:
            # Use the enhanced Gemini-only document analysis
            analysis_result = reasoning_engine.analyze_legal_document(
                document_text, 
                analysis_type=analysis_type,
                query=query  # For Q&A mode
            )
            
            if not analysis_result.get('success', False):
                raise Exception(analysis_result.get('error', 'Analysis failed'))
            
            # Build response with full analysis results
            response_data = {
                'document_id': doc_id,
                'filename': doc.filename,
                'analysis_type': analysis_type,
                'analysis': analysis_result.get('analysis', ''),
                'metadata': {
                    'char_count': document_metadata.get('char_count'),
                    'word_count': document_metadata.get('word_count'),
                    'file_type': document_metadata.get('file_type')
                }
            }
            
            # Add key elements if available
            if 'key_elements' in analysis_result:
                response_data['key_elements'] = analysis_result['key_elements']
            
            # Add query info for Q&A mode
            if analysis_type == 'qa' and query:
                response_data['query'] = query
                response_data['chunks_used'] = analysis_result.get('chunks_used', 0)
            
            # Add chunks info for comprehensive analysis
            if 'chunks_analyzed' in analysis_result:
                response_data['chunks_analyzed'] = analysis_result['chunks_analyzed']
            
        except Exception as analysis_error:
            print(f"Analysis error: {str(analysis_error)}")
            import traceback
            traceback.print_exc()
            session.close()
            return jsonify({
                'error': f'Analysis failed: {str(analysis_error)}'
            }), 500
        
        session.close()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Document analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
@auth_manager.token_required
def list_documents():
    """List user's documents"""
    try:
        user_id = request.current_user['user_id']
        
        session = get_session(engine)
        docs = session.query(Document).filter_by(user_id=user_id).all()
        
        documents = [{
            'id': doc.id,
            'filename': doc.filename,
            'file_type': doc.file_type,
            'uploaded_at': doc.uploaded_at.isoformat(),
            'processed': doc.processed
        } for doc in docs]
        
        session.close()
        
        return jsonify({'documents': documents}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== Query Routes ==============

@app.route('/api/query', methods=['POST'])
@auth_manager.token_required
def handle_query():
    """Handle legal query with validation and semantic short answer"""
    session = None
    try:
        data = request.get_json()
        query_text = data.get('query')
        response_mode = data.get('mode', 'short')  # 'short' or 'detailed'
        
        if not query_text:
            return jsonify({'error': 'Query is required'}), 400
        
        # Basic validation
        if len(query_text.strip()) < 10:
            return jsonify({
                'error': 'Query too short. Please provide more details.',
                'suggestions': 'Try to be more specific about your legal question.'
            }), 400
        
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        # Check if API key is configured
        if not Config.GOOGLE_API_KEY or not reasoning_engine:
            return jsonify({
                'error': 'AI service not available. Please configure GOOGLE_API_KEY in .env file and restart the server.'
            }), 503
        
        # Step 1: Validate query with user role context
        validation_result = None
        original_query = query_text
        query_was_reiterated = False
        
        try:
            validation_result = reasoning_engine.validate_query(query_text, user_role)
            print(f"Query validation: {validation_result}")
            
            # Check if query is valid
            if not validation_result.get('validated', True):
                return jsonify({
                    'error': 'Query validation failed',
                    'validation': validation_result,
                    'suggestions': validation_result.get('suggestions', 'Please rephrase your question.')
                }), 400
            
            # Warn if not clearly legal
            if not validation_result.get('is_legal', True):
                return jsonify({
                    'warning': 'This does not appear to be a legal question',
                    'validation': validation_result,
                    'suggestions': 'Please ask a question related to Indian law.'
                }), 400
            
            # Step 2: Check quality score and clarity
            quality_score = validation_result.get('quality_score', 10)
            is_clear = validation_result.get('is_clear', 'yes')
            
            # If quality score < 8 or needs clarification, use reiterated query
            if quality_score < 8 or is_clear == 'needs_clarification':
                reiterated_query = validation_result.get('reiterated_query', '')
                if reiterated_query and reiterated_query != query_text:
                    print(f"Query reiterated: '{query_text}' -> '{reiterated_query}'")
                    query_text = reiterated_query
                    query_was_reiterated = True
                
        except Exception as val_error:
            print(f"Validation warning: {str(val_error)}")
            # Continue even if validation fails
            validation_result = {'validated': True, 'quality_score': 5}
        
        # Step 2: Search for relevant cases (with error handling)
        cases = []
        try:
            cases = legal_retriever.search_cases(query_text, limit=5)
        except Exception as case_error:
            print(f"Warning: Case search failed: {str(case_error)}")
            cases = []
        
        # Step 2.5: Search relevant documents using RAG (NEW!)
        document_context = []
        if rag_tool:
            try:
                doc_search = rag_tool.semantic_search_all(query_text, top_k=5)
                if doc_search.get('success') and doc_search.get('documents'):
                    document_context = doc_search['documents'][:3]  # Top 3 relevant docs
                    print(f"Found {len(document_context)} relevant documents in RAG")
            except Exception as rag_error:
                print(f"Warning: RAG search failed: {str(rag_error)}")
        
        # Step 3: Build context
        session = get_session(engine)
        memory_mgr = MemoryManager(session)
        user_context = memory_mgr.build_user_context(user_id, user_role)
        
        # Add case context
        if cases:
            user_context += "\n\nRelevant Cases:\n"
            for i, case in enumerate(cases[:3], 1):
                user_context += f"{i}. {case.get('title', 'N/A')}\n"
        
        # Add document context from RAG (NEW!)
        if document_context:
            user_context += "\n\nRelevant Documents from Knowledge Base:\n"
            for i, doc in enumerate(document_context, 1):
                user_context += f"{i}. {doc.get('title', 'N/A')} (Relevance: {doc.get('max_similarity', 0):.2f})\n"
                # Add top chunk preview
                if doc.get('top_chunks'):
                    preview = doc['top_chunks'][0].get('text', '')[:150]
                    user_context += f"   Preview: {preview}...\n"
        
        # Step 4: Generate response based on mode
        response_text = ""
        try:
            if response_mode == 'short':
                # Generate semantic short answer
                response_text = reasoning_engine.generate_semantic_short_answer(
                    query_text,
                    user_context,
                    user_role,
                    max_words=150
                )
            else:
                # Generate detailed answer
                response_text = reasoning_engine.generate_legal_advice(
                    query_text,
                    user_context,
                    user_role
                )
        except Exception as ai_error:
            print(f"AI Error: {str(ai_error)}")
            import traceback
            traceback.print_exc()
            # Fallback response
            response_text = f"I understand you're asking about: {query_text}\n\n"
            response_text += "However, I'm currently experiencing technical difficulties. "
            response_text += "Please try again or rephrase your question.\n\n"
            response_text += f"Error: {str(ai_error)}"
        
        # Step 5: Store query
        try:
            new_query = Query(
                user_id=user_id,
                query_text=query_text,
                response_text=response_text
            )
            
            session.add(new_query)
            session.commit()
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            # Continue even if storage fails
        
        # Build response
        response_data = {
            'query': query_text,
            'original_query': original_query if query_was_reiterated else None,
            'query_reiterated': query_was_reiterated,
            'response': response_text,
            'mode': response_mode,
            'related_cases': cases[:3] if cases else [],
            'related_documents': [  # NEW: Include document context
                {
                    'doc_id': doc.get('doc_id'),
                    'title': doc.get('title'),
                    'relevance': doc.get('max_similarity', 0),
                    'preview': doc.get('top_chunks', [{}])[0].get('text', '')[:200] if doc.get('top_chunks') else ''
                }
                for doc in document_context
            ] if document_context else []
        }
        
        # Add validation info if available
        if validation_result:
            response_data['validation'] = {
                'quality_score': validation_result.get('quality_score', 'N/A'),
                'legal_domain': validation_result.get('legal_domain', 'general'),
                'is_clear': validation_result.get('is_clear', 'yes')
            }
            
            # Include suggestions if quality was low
            if validation_result.get('quality_score', 10) < 8:
                response_data['validation']['suggestions'] = validation_result.get('suggestions', '')
        
        # Add hint about using agent for complex document operations
        if document_context and len(document_context) > 0:
            response_data['hint'] = 'Multiple relevant documents found. Use /api/agent/query for complex document analysis.'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Query handler error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'details': 'Please check server logs for more information'
        }), 500
    finally:
        if session:
            try:
                session.close()
            except:
                pass

# ============== Legal Research Routes ==============

@app.route('/api/research/cases', methods=['GET'])
@auth_manager.token_required
def search_cases():
    """Search legal cases"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        cases = legal_retriever.search_cases(query, limit)
        
        return jsonify({'cases': cases}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/case/<case_id>', methods=['GET'])
@auth_manager.token_required
def get_case(case_id):
    """Get case details"""
    try:
        case = legal_retriever.get_case_details(case_id)
        
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        return jsonify({'case': case}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== Health Check ==============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'LuminaryAI',
        'version': '1.0.0',
        'ai_modules': {
            'reasoning_engine': reasoning_engine is not None,
            'orchestrator': orchestrator is not None,
            'rag_tool': rag_tool is not None,
            'api_key_configured': bool(Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_gemini_api_key_here')
        }
    }), 200

@app.route('/api/agent/query', methods=['POST'])
@auth_manager.token_required
def agent_query():
    """
    Intelligent agent endpoint - LLM autonomously decides which tools to use
    Handles document management, search, and analysis automatically
    """
    try:
        if not langchain_tools or not orchestrator:
            return jsonify({
                'error': 'Agent not available. Please configure GOOGLE_API_KEY and restart.'
            }), 503
        
        data = request.get_json()
        query = data.get('query')
        verbose = data.get('verbose', False)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        # Import LangChain agent components
        from langchain.agents import AgentExecutor, create_react_agent
        from langchain_classic.prompts import PromptTemplate
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Create LLM
        llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.7
        )
        
        # Role-specific context
        role_context = {
            "lawyer": "You are assisting a practicing lawyer. Provide detailed legal analysis.",
            "student": "You are assisting a law student. Explain concepts clearly with examples.",
            "public": "You are assisting a member of the public. Use simple, accessible language."
        }
        context = role_context.get(user_role, role_context["public"])
        
        # Create prompt template
        template = f"""You are LuminaryAI, an intelligent legal assistant specializing in Indian law.

{context}

You have access to document management tools that allow you to:
- Add documents to the knowledge base
- Search for relevant information across documents
- Query specific documents for answers
- Compare documents
- List and manage documents

Available tools:
{{tools}}

Tool names: {{tool_names}}

Always:
1. Think step-by-step about what tools you need
2. Use tools when document operations are mentioned
3. Provide accurate, source-based answers
4. Be clear about document IDs when referencing specific documents
5. Cite sources from documents when answering

User Question: {{input}}

{{agent_scratchpad}}"""

        prompt = PromptTemplate.from_template(template)
        
        # Create agent
        agent = create_react_agent(llm, langchain_tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=langchain_tools,
            verbose=verbose,
            max_iterations=15,
            handle_parsing_errors=True,
            early_stopping_method="generate"
        )
        
        # Execute agent
        result = agent_executor.invoke({"input": query})
        
        return jsonify({
            'query': query,
            'answer': result.get('output', ''),
            'user_role': user_role,
            'agent_type': 'autonomous',
            'tools_available': len(langchain_tools),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Agent error: {str(e)}")
        return jsonify({
            'error': f'Agent execution failed: {str(e)}'
        }), 500

@app.route('/api/status', methods=['GET'])
def status_check():
    """Detailed status check endpoint"""
    status = {
        'database': 'unknown',
        'ai_modules': {
            'reasoning_engine': reasoning_engine is not None,
            'orchestrator': orchestrator is not None,
            'rag_tool': rag_tool is not None,
            'langchain_tools': langchain_tools is not None and len(langchain_tools) if langchain_tools else 0
        },
        'config': {
            'api_key_configured': bool(Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_gemini_api_key_here'),
            'upload_folder_exists': os.path.exists(Config.UPLOAD_FOLDER)
        }
    }
    
    # Test database
    try:
        session = get_session(engine)
        session.execute('SELECT 1')
        session.close()
        status['database'] = 'connected'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
    
    return jsonify(status), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Welcome to LuminaryAI API - Intelligent Legal Assistant with Document Management',
        'version': '2.0.0',
        'features': {
            'document_rag': 'Semantic document search and Q&A',
            'intelligent_agent': 'Autonomous document management via LLM',
            'role_based': 'Tailored responses for lawyers, students, and public',
            'indian_law': 'Specialized in Indian legal system',
            'multi_modal': 'PDF, DOCX, TXT document support'
        },
        'endpoints': {
            'auth': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login'
            },
            'documents': {
                'upload': 'POST /api/documents/upload',
                'list': 'GET /api/documents',
                'analyze': 'POST /api/documents/analyze'
            },
            'query': {
                'basic': 'POST /api/query (document-aware)',
                'agent': 'POST /api/agent/query (autonomous agent) 🤖'
            },
            'rag': {
                'add_document': 'POST /api/rag/documents',
                'search': 'POST /api/rag/search',
                'query_doc': 'POST /api/rag/documents/<id>/query',
                'list_docs': 'GET /api/rag/documents',
                'compare': 'POST /api/rag/documents/compare',
                'statistics': 'GET /api/rag/statistics'
            },
            'research': {
                'search_cases': 'GET /api/research/cases'
            },
            'health': {
                'check': 'GET /api/health',
                'status': 'GET /api/status'
            }
        },
        'documentation': {
            'rag_tool': 'See DOCUMENT_RAG_TOOL.md',
            'langchain': 'See LANGCHAIN_INTEGRATION.md',
            'quick_start': 'See QUICK_START_RAG.md'
        }
    }), 200

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=app.config['FLASK_PORT'],
        debug=app.config['DEBUG']
    )
