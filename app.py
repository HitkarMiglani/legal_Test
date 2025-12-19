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
# from modules.orchestrator import LangChainOrchestrator
from modules.reasoning_engine import GeminiReasoningEngine
from modules.document_rag_chromadb import ChromaDBRAGTool
from modules.document_rag_langchain import create_document_rag_tools
from modules.document_rag_routes import rag_bp
# from modules.agent_graph import create_agent_graph

# Import utilities
from utils.logger import logger, setup_logger
from utils.exceptions import (
    LuminaryException,
    ValidationError,
    NotFoundError,
    AIServiceError,
    DocumentProcessingError
)
from utils.middleware import request_logging_middleware

# Setup logger
logger = setup_logger('luminary', Config.LOG_LEVEL, Config.LOG_FILE)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])
CORS(app)

# Apply middleware
# Note: request_logging_middleware includes global exception handler
request_logging_middleware(app)

# Import uuid for generating document IDs
import uuid

# Initialize database
engine = init_db(app.config['DB_URL'])

# Initialize modules with error handling
doc_processor = DocumentProcessor(app.config['UPLOAD_FOLDER'])
legal_retriever = LegalRetriever()
# orchestrator = None
reasoning_engine = None
rag_tool = None
rag_tool = None
langchain_tools = None
# agent_graph = None

# Initialize AI modules with proper error handling
try:
    if Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_gemini_api_key_here':
        # orchestrator = LangChainOrchestrator()
        reasoning_engine = GeminiReasoningEngine()
        
        # Initialize Document RAG Tool with ChromaDB (no API quota limits!)
        rag_tool = ChromaDBRAGTool(storage_path="chromadb_storage", model_name="all-MiniLM-L6-v2")
        langchain_tools = create_document_rag_tools(rag_tool=rag_tool)
        
        logger.info("AI modules initialized successfully")
        logger.info(f"Document RAG Tool initialized with {len(langchain_tools)} LangChain tools")
        
        # Initialize LangGraph Agent
        # agent_graph = create_agent_graph()
        logger.info("LangGraph Agent initialized successfully")
    else:
        logger.warning("GOOGLE_API_KEY not configured. AI features will be limited.")
        logger.warning("Please set your API key in the .env file.")
except Exception as e:
    logger.error(f"Failed to initialize AI modules: {str(e)}", exc_info=True)
    logger.warning("The application will run with limited functionality.")

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register Document RAG API routes
from modules.document_rag_routes import init_rag_routes
app.register_blueprint(rag_bp)
init_rag_routes(rag_tool)  # Pass the shared rag_tool instance
logger.info("Document RAG API routes registered at /api/rag/*")

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

@app.route('/api/user/<int:user_id>/history', methods=['GET'])
@auth_manager.token_required
def get_user_history(user_id):
    """Get user's chat history from database"""
    try:
        # Verify user can only access their own history
        if request.current_user['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        session = get_session(engine)
        
        # Get recent queries (last 50)
        queries = session.query(Query).filter_by(user_id=user_id).order_by(Query.created_at.desc()).limit(50).all()
        
        # Build chat history
        chat_history = []
        agent_history = []
        
        for query in reversed(queries):  # Reverse to get chronological order
            # Determine if it's an agent query based on response content
            is_agent = 'agent_info' in (query.response_text or '') or 'LangGraph' in (query.response_text or '')
            
            history_item = {
                'role': 'user',
                'content': query.query_text,
                'timestamp': query.created_at.isoformat() if query.created_at else None
            }
            
            response_item = {
                'role': 'assistant',
                'content': query.response_text,
                'timestamp': query.created_at.isoformat() if query.created_at else None
            }
            
            if is_agent:
                agent_history.append(history_item)
                agent_history.append(response_item)
            else:
                chat_history.append(history_item)
                chat_history.append(response_item)
        
        # Get user preferences from memory
        memory_mgr = MemoryManager(session)
        user_memories = memory_mgr.get_all_memories(user_id)
        
        session.close()
        
        return jsonify({
            'chat_history': chat_history,
            'agent_history': agent_history,
            'preferences': user_memories,
            'total_queries': len(queries)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user history: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>/preferences', methods=['GET', 'POST'])
@auth_manager.token_required
def manage_preferences(user_id):
    """Get or update user preferences using MemoryManager"""
    try:
        # Verify user can only access their own preferences
        if request.current_user['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        session = get_session(engine)
        memory_mgr = MemoryManager(session)
        
        if request.method == 'GET':
            # Get all preferences
            preferences = memory_mgr.get_all_memories(user_id)
            session.close()
            return jsonify({'preferences': preferences}), 200
        
        elif request.method == 'POST':
            # Update preferences
            data = request.get_json()
            
            if not data or 'key' not in data or 'value' not in data:
                session.close()
                return jsonify({'error': 'Missing key or value'}), 400
            
            key = data['key']
            value = data['value']
            
            success = memory_mgr.store_memory(user_id, key, value)
            session.close()
            
            if success:
                return jsonify({'message': 'Preference saved', 'key': key}), 200
            else:
                return jsonify({'error': 'Failed to save preference'}), 500
                
    except Exception as e:
        logger.error(f"Error managing preferences: {str(e)}", exc_info=True)
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
        
        # Generate unique document ID (UUID)
        doc_id = str(uuid.uuid4())
        
        # Create document record in database
        session = get_session(engine)
        
        new_doc = Document(
            doc_id=doc_id,
            user_id=user_id,
            filename=filename,
            file_type=file_ext,
            file_path=file_path,
            processed='processing',
        )
        
        session.add(new_doc)
        session.commit()
        session.close()
        
        # Process document (in background in production)
        try:
            # print(f"Processing document: {filename} (type: {file_ext})")
            result = doc_processor.process_document(file_path, file_ext)
            
            # print(f"Document processed successfully. Metadata: {result['metadata']}")
            
            # Validate extraction
            if result['metadata']['char_count'] == 0:
                raise Exception("No text content extracted. PDF may be image-based or corrupted. Try OCR or text-based PDF.")
            
            # Cache the extracted text and metadata in database
            session = get_session(engine)
            doc = session.query(Document).filter_by(doc_id=doc_id).first()
            if doc:
                import json
                doc.cached_text = result['text']
                doc.cached_metadata = json.dumps(result['metadata'])
                session.commit()
                # print(f"💾 Cached extracted text ({result['metadata']['char_count']} chars) in database")
            session.close()
            
            # Add to RAG system (ChromaDB)
            if rag_tool:
                try:
                    logger.info(f"Adding document to RAG system...")
                    rag_result = rag_tool.add_document(
                        content=result['text'],
                        title=filename,
                        metadata={
                            'file_type': file_ext,
                            'user_id': user_id,
                            'uploaded_at': datetime.utcnow().isoformat()
                        },
                        doc_id=doc_id  # Use the UUID from database
                    )
                    logger.info(f"✅ Document {doc_id} added to RAG system successfully")
                except Exception as rag_error:
                    logger.error(f"Failed to add document to RAG system: {str(rag_error)}")
                    # Continue even if RAG fails
            
            
            # Update document status
            session = get_session(engine)
            doc = session.query(Document).filter_by(doc_id=doc_id).first()
            doc.processed = 'completed'
            session.commit()
            session.close()
            
            print(f"Document upload complete: {doc_id}")
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document_id': doc_id,
                'metadata': result['metadata'],
                'filename': filename,
                'chunks_count': len(result.get('chunks', []))
            }), 200
            
        except Exception as e:
            print(f"Document processing error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            session = get_session(engine)
            doc = session.query(Document).filter_by(doc_id=doc_id).first()
            if doc:
                doc.processed = 'failed'
                session.commit()
            session.close()
            
            return jsonify({
                'error': f'Processing failed: {str(e)}',
                'suggestion': 'If PDF is image-based, please convert to text-based PDF or use OCR'
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<doc_id>/analyze', methods=['POST'])
@auth_manager.token_required
def analyze_document(doc_id):
    """Analyze a document using enhanced Gemini-only processing with timeout handling"""
    import time
    start_time = time.time()
    
    try:
        data = request.get_json() or {}
        query = data.get('query', "Summarize the Document")
        analysis_type = data.get('type', 'summary')  # Default to 'summary' for faster response
        
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        session = get_session(engine)
        
        # Get document by doc_id (UUID)
        doc = session.query(Document).filter_by(doc_id=doc_id, user_id=user_id).first()
        
        if not doc:
            session.close()
            return jsonify({'error': 'Document not found'}), 400
        
        # Check if Gemini reasoning engine is available
        if not reasoning_engine:
            session.close()
            return jsonify({
                'error': 'AI service not available. Please configure GOOGLE_API_KEY in .env file and restart the server.'
            }), 503
        
        print(f"⏱️  Analysis started at {time.time() - start_time:.2f}s")
        
        # Check if document already processed (use cached text if available)
        import json
        try:
            if doc.cached_text and doc.cached_metadata:
                print(f"✨ Using cached text from database")
                document_text = doc.cached_text
                document_metadata = json.loads(doc.cached_metadata)
                # Still need to generate chunks
                chunks = doc_processor.chunk_text(document_text)
                print(f"✅ Cached text loaded: {document_metadata['char_count']} chars, {len(chunks)} chunks in {time.time() - start_time:.2f}s")
            else:
                # Process document to extract text
                print(f"📄 Extracting text from: {doc.file_path}")
                result = doc_processor.process_document(doc.file_path, doc.file_type)
                document_text = result['text']
                document_metadata = result['metadata']
                
                # Cache for future use
                doc.cached_text = document_text
                doc.cached_metadata = json.dumps(document_metadata)
                session.commit()
                print(f"💾 Cached text in database for future use")
                print(f"✅ Text extracted: {document_metadata['char_count']} chars in {time.time() - start_time:.2f}s")
        except Exception as extract_error:
            print(f"❌ Text extraction failed: {str(extract_error)}")
            session.close()
            return jsonify({
                'error': f'Failed to extract text: {str(extract_error)}'
            }), 500
        
        # For large documents (>8k chars), force summary mode to avoid timeout
        if document_metadata['char_count'] > 8000 and analysis_type == 'comprehensive':
            print(f"⚠️  Large document detected ({document_metadata['char_count']} chars), using summary mode")
            analysis_type = 'summary'
            query = "Provide a concise summary of this document with key points"
        
        # Add timeout check - if already taking too long, use fast mode
        elapsed = time.time() - start_time
        if elapsed > 5:
            print(f"⚠️  Already at {elapsed:.2f}s, forcing fast summary mode")
            analysis_type = 'summary'

        # Perform enhanced Gemini-based analysis with timeout monitoring
        try:
            print(f"🤖 Starting {analysis_type} analysis at {time.time() - start_time:.2f}s")
            
            # Use the enhanced Gemini-only document analysis
            analysis_result = reasoning_engine.analyze_legal_document(
                document_text, 
                analysis_type=analysis_type,
                query=query  # For Q&A mode
            )
            
            print(f"✅ Analysis completed in {time.time() - start_time:.2f}s")
            
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
            'id': doc.doc_id,
            'doc_id': doc.doc_id,
            'filename': doc.filename,
            'file_type': doc.file_type,
            'uploaded_at': doc.uploaded_at.isoformat(),
            'processed': doc.processed
        } for doc in docs]
        
        session.close()
        
        return jsonify({'documents': documents}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<doc_id>', methods=['GET'])
@auth_manager.token_required
def get_document(doc_id):
    """Get specific document by doc_id"""
    try:
        user_id = request.current_user['user_id']
        
        session = get_session(engine)
        doc = session.query(Document).filter_by(doc_id=doc_id, user_id=user_id).first()
        
        if not doc:
            session.close()
            return jsonify({'error': 'Document not found'}), 404
        
        document = {
            'id': doc.doc_id,
            'doc_id': doc.doc_id,
            'filename': doc.filename,
            'file_type': doc.file_type,
            'uploaded_at': doc.uploaded_at.isoformat(),
            'processed': doc.processed,
            'file_path': doc.file_path
        }
        
        session.close()
        
        return jsonify(document), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== Query Routes ==============

@app.route('/api/chat', methods=['POST'])
@auth_manager.token_required
def handle_smart_chat():
    """Unified smart chat endpoint - auto-detects whether to use simple or agentic mode"""
    session = None
    try:
        data = request.get_json()
        query_text = data.get('query')
        force_mode = data.get('mode', 'auto')  # 'auto', 'simple', or 'agent'
        
        if not query_text or len(query_text.strip()) < 5:
            return jsonify({'error': 'Please provide a more detailed query'}), 400
        
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        session = get_session(engine)
        memory_mgr = MemoryManager(session)
        user_context = memory_mgr.build_user_context(user_id, user_role)
        
        # Auto-detect mode if not forced
        if force_mode == 'auto':
            # Check if user has documents
            user = session.query(User).filter_by(id=user_id).first()
            has_documents = user and session.query(Document).filter_by(user_id=user_id).count() > 0
            
            # Use agent if:
            # 1. User has documents (might need RAG search)
            # 2. Query is complex (more than 20 words)
            # 3. Query contains tool-related keywords
            word_count = len(query_text.split())
            tool_keywords = ['find', 'search', 'compare', 'analyze', 'cases', 'document', 'precedent']
            needs_tools = any(keyword in query_text.lower() for keyword in tool_keywords)
            
            use_agent = has_documents or word_count > 20 or needs_tools
            mode = 'agent' if use_agent else 'simple'
        else:
            mode = force_mode
        
        logger.info(f"💬 Smart chat using {mode} mode for: {query_text[:100]}...")
        
        # Route to appropriate handler
        if mode == 'agent':
            # Use Agno agent with knowledge base
            from modules.agno_agent import create_legal_agent
            agent = create_legal_agent(user_role=user_role)
            result = agent.query_sync(query=query_text, context=user_context)
            
            if not result.get('success'):
                # Fallback to simple mode if agent fails
                logger.warning("Agent failed, falling back to simple mode")
                mode = 'simple'
            else:
                response_text = result.get('response', '')
                
                # Save to database
                query_obj = Query(
                    user_id=user_id,
                    query_text=query_text,
                    response_text=response_text,
                    context=user_context
                )
                session.add(query_obj)
                session.commit()
                
                return jsonify({
                    'query': query_text,
                    'response': response_text,
                    'mode': 'agent',
                    'features': ['knowledge_search', 'RAG', 'role_based'],
                    'timestamp': result.get('timestamp')
                }), 200
        
        # Simple mode (fallback or auto-detected)
        if mode == 'simple':
            # Validate query
            validation_result = reasoning_engine.validate_query(query_text, user_role) if reasoning_engine else {'validated': True}
            
            if not validation_result.get('validated', True):
                return jsonify({
                    'error': 'Invalid query',
                    'suggestions': validation_result.get('suggestions', 'Please rephrase')
                }), 400
            
            # Search cases
            cases = []
            try:
                cases = legal_retriever.search_cases(query_text, limit=3)
            except:
                pass
            
            # Search documents
            document_context = []
            if rag_tool:
                try:
                    doc_search = rag_tool.semantic_search_all(query_text, top_k=3)
                    if doc_search.get('success'):
                        document_context = doc_search.get('documents', [])[:3]
                except:
                    pass
            
            # Generate response
            if reasoning_engine:
                response_text = reasoning_engine.generate_answer(
                    query=query_text,
                    cases=cases,
                    role=user_role,
                    context=user_context,
                    document_context=document_context
                )
            else:
                response_text = "AI service unavailable. Please configure GOOGLE_API_KEY."
            
            # Save to database
            query_obj = Query(
                user_id=user_id,
                query_text=query_text,
                response_text=response_text,
                context=user_context
            )
            session.add(query_obj)
            session.commit()
            
            return jsonify({
                'query': query_text,
                'response': response_text,
                'mode': 'simple',
                'features': ['case_search', 'document_search', 'role_based'],
                'cases_found': len(cases),
                'documents_found': len(document_context)
            }), 200
    
    except Exception as e:
        logger.error(f"Smart chat error: {str(e)}", exc_info=True)
        if session:
            session.rollback()
        return jsonify({'error': f'Chat processing failed: {str(e)}'}), 500
    finally:
        if session:
            session.close()

# Legacy endpoints (deprecated - use /api/chat instead)
@app.route('/api/query', methods=['POST'])
@auth_manager.token_required
def handle_query():
    """⚠️ DEPRECATED: Use /api/chat instead. This endpoint will be removed in future versions."""
    # Forward to smart chat with simple mode
    data = request.get_json()
    data['mode'] = 'simple'
    request._cached_json = (data, data)
    return handle_smart_chat()

@app.route('/api/agent/query', methods=['POST'])
@auth_manager.token_required
def handle_agent_query():
    """⚠️ DEPRECATED: Use /api/chat instead. This endpoint will be removed in future versions."""
    # Forward to smart chat with agent mode
    data = request.get_json()
    data['mode'] = 'agent'
    request._cached_json = (data, data)
    return handle_smart_chat()


# Original query endpoint (commented for reference - can be deleted later)
"""
@app.route('/api/query', methods=['POST'])
# Original query endpoint (commented for reference - can be deleted later)
"""
"""
Old implementation removed - see git history if needed
All old /api/query and /api/agent/query logic is now in /api/chat (handle_smart_chat)
"""

# ============== Document RAG Routes ==============

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

@app.route('/api/health')
def health_check():
    """Comprehensive health check endpoint"""
    import time
    import psutil
    
    health_status = {
        'status': 'healthy',
        'service': 'LuminaryAI',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {}
    }
    
    overall_healthy = True
    
    # Database check
    try:
        from sqlalchemy import text
        session = get_session(engine)
        session.execute(text('SELECT 1'))
        session.close()
        health_status['checks']['database'] = {'status': 'healthy', 'message': 'Connected'}
    except Exception as e:
        health_status['checks']['database'] = {'status': 'unhealthy', 'message': str(e)}
        overall_healthy = False
    
    # AI modules check
    ai_modules_status = {
        'reasoning_engine': reasoning_engine is not None,
        # 'orchestrator': orchestrator is not None,
        'rag_tool': rag_tool is not None,
        'langchain_tools': langchain_tools is not None and len(langchain_tools) > 0 if langchain_tools else False,
        'api_key_configured': bool(Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_gemini_api_key_here')
    }
    health_status['checks']['ai_modules'] = ai_modules_status
    
    if not ai_modules_status['api_key_configured']:
        health_status['checks']['ai_modules']['status'] = 'degraded'
        health_status['checks']['ai_modules']['message'] = 'API key not configured'
    
    # Storage check
    try:
        import os
        uploads_exists = os.path.exists(app.config['UPLOAD_FOLDER'])
        health_status['checks']['storage'] = {
            'status': 'healthy' if uploads_exists else 'unhealthy',
            'uploads_folder': uploads_exists,
            'message': 'Storage accessible' if uploads_exists else 'Uploads folder missing'
        }
        if not uploads_exists:
            overall_healthy = False
    except Exception as e:
        health_status['checks']['storage'] = {'status': 'unhealthy', 'message': str(e)}
        overall_healthy = False
    
    # System resources
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        health_status['checks']['system'] = {
            'status': 'healthy',
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': round(memory.available / 1024 / 1024, 2)
        }
        if cpu_percent > 90 or memory.percent > 90:
            health_status['checks']['system']['status'] = 'warning'
            overall_healthy = False
    except ImportError:
        health_status['checks']['system'] = {'status': 'unknown', 'message': 'psutil not available'}
    except Exception as e:
        health_status['checks']['system'] = {'status': 'error', 'message': str(e)}
    
    health_status['status'] = 'healthy' if overall_healthy else 'degraded'
    
    status_code = 200 if overall_healthy else 503
    
    return jsonify(health_status), status_code

# @app.route('/api/agent/query', methods=['POST'])
# @auth_manager.token_required
# def agent_query():
#     """
#     LangGraph-based intelligent agent endpoint
#     Uses state-based graph workflow for autonomous tool selection and execution
#     """
#     session = None
#     try:
#         # Validate availability
#         if not langchain_tools or not orchestrator:
#             return jsonify({
#                 'error': 'Agent not available. Please configure GOOGLE_API_KEY and restart.'
#             }), 503
        
#         # Parse request
#         data = request.get_json()
#         query_text = data.get('query')
#         max_iterations = data.get('max_iterations', 10)
#         verbose = data.get('verbose', False)
#         stream = data.get('stream', False)  # Future: streaming support
        
#         if not query_text:
#             return jsonify({'error': 'Query is required'}), 400
        
#         if len(query_text.strip()) < 5:
#             return jsonify({'error': 'Query too short. Please provide more details.'}), 400
        
#         user_id = request.current_user['user_id']
#         user_role = request.current_user['role']
        
#         # Initialize session and memory manager
#         session = get_session(engine)
#         memory_mgr = MemoryManager(session)
#         user_context = memory_mgr.build_user_context(user_id, user_role)
        
#         # Import LangGraph components
#         from typing import TypedDict, Annotated, Sequence
#         from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
#         from langchain_google_genai import ChatGoogleGenerativeAI
#         from langchain_classic.tools import Tool
#         from langgraph.graph import StateGraph, END
#         from langgraph.prebuilt import ToolNode
#         import operator
        
#         # Define agent state
#         class AgentState(TypedDict):
#             """State of the agent workflow"""
#             messages: Annotated[Sequence[BaseMessage], operator.add]
#             user_query: str
#             user_role: str
#             iterations: int
#             max_iterations: int
#             final_answer: str
#             tools_used: list
#             execution_log: list
        
#         # Initialize LLM
#         llm = ChatGoogleGenerativeAI(
#             model=Config.LLM_MODEL,
#             google_api_key=Config.GOOGLE_API_KEY,
#             temperature=0.3,
#             max_output_tokens=2048
#         )
        
#         # Prepare tools
#         available_tools = []
#         tool_names = []
        
#         # Add RAG tools
#         if langchain_tools:
#             available_tools.extend(langchain_tools)
#             tool_names.extend([tool.name for tool in langchain_tools])
#             logger.info(f"Added {len(langchain_tools)} RAG tools: {tool_names}")
        
#         # Add case search tool
#         def search_legal_cases(query: str) -> str:
#             """Search for relevant Indian legal cases"""
#             try:
#                 cases = legal_retriever.search_cases(query, limit=5)
#                 if not cases:
#                     return "No relevant cases found."
                
#                 output = f"Found {len(cases)} relevant cases:\n\n"
#                 for i, case in enumerate(cases, 1):
#                     output += f"{i}. {case.get('title', 'N/A')}\n"
#                     output += f"   Court: {case.get('court', 'N/A')}\n"
#                     output += f"   Summary: {case.get('summary', 'N/A')[:200]}...\n\n"
#                 return output
#             except Exception as e:
#                 return f"Error searching cases: {str(e)}"
        
#         case_search_tool = Tool(
#             name="search_legal_cases",
#             func=search_legal_cases,
#             description="Search for relevant Indian legal cases and precedents. Input: search query string. Returns: List of relevant cases with summaries."
#         )
#         available_tools.append(case_search_tool)
#         tool_names.append("search_legal_cases")
        
#         logger.info(f"Total tools available: {len(available_tools)} - {tool_names}")
        
#         # Bind tools to LLM
#         llm_with_tools = llm.bind_tools(available_tools)
        
#         # Define agent nodes
#         def agent_node(state: AgentState) -> AgentState:
#             """Main agent reasoning node"""
#             # Role-specific context
#             role_context = {
#                 "LAWYER": "You are assisting a practicing lawyer. Provide detailed legal analysis with case law references.",
#                 "STUDENT": "You are assisting a law student. Explain legal concepts clearly with educational context.",
#                 "PUBLIC": "You are assisting a member of the public. Use simple, accessible language.",
#                 # Fallback for lowercase (backwards compatibility)
#                 "lawyer": "You are assisting a practicing lawyer. Provide detailed legal analysis with case law references.",
#                 "student": "You are assisting a law student. Explain legal concepts clearly with educational context.",
#                 "public": "You are assisting a member of the public. Use simple, accessible language."
#             }
            
#             system_prompt = f"""You are LuminaryAI, an intelligent legal assistant specializing in Indian law.

# {role_context.get(state['user_role'], role_context['PUBLIC'])}

# User Context and Preferences:
# {user_context}

# You have access to tools for:
# - Searching and querying documents in the knowledge base
# - Finding relevant legal cases and precedents
# - Comparing documents
# - Managing document collection

# When answering:
# 1. Use tools to gather information when needed
# 2. Cite sources (document IDs, case names) when using retrieved information
# 3. Provide structured, comprehensive answers
# 4. Be clear about what information comes from which source
# 5. If you don't have enough information, use search tools to find it
# 6. Consider user preferences and previous interactions from their context

# Current iteration: {state['iterations']}/{state['max_iterations']}
# """
            
#             messages = [HumanMessage(content=system_prompt)] + state['messages']
            
#             # Call LLM with tools
#             response = llm_with_tools.invoke(messages)
            
#             # Log execution
#             execution_entry = {
#                 'iteration': state['iterations'],
#                 'type': 'agent_reasoning',
#                 'content': response.content if hasattr(response, 'content') else str(response)[:200]
#             }
            
#             return {
#                 "messages": [response],
#                 "iterations": state['iterations'] + 1,
#                 "execution_log": state['execution_log'] + [execution_entry]
#             }
        
#         def tool_node(state: AgentState) -> AgentState:
#             """Execute tools called by the agent"""
#             last_message = state['messages'][-1]
            
#             # Check if there are tool calls
#             if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
#                 return state
            
#             # Execute each tool call
#             tool_messages = []
#             tools_used = state.get('tools_used', [])
#             execution_log = state.get('execution_log', [])
            
#             # Create tool executor
#             tool_executor = ToolNode(available_tools)
            
#             for tool_call in last_message.tool_calls:
#                 tool_name = tool_call.get('name', 'unknown')
#                 tools_used.append(tool_name)
                
#                 # Execute tool
#                 try:
#                     result = tool_executor.invoke(state)
                    
#                     # Log execution
#                     execution_log.append({
#                         'iteration': state['iterations'],
#                         'type': 'tool_execution',
#                         'tool': tool_name,
#                         'input': str(tool_call.get('args', {}))[:200],
#                         'success': True
#                     })
                    
#                     return result
                    
#                 except Exception as tool_error:
#                     logger.error(f"Tool execution error: {str(tool_error)}")
                    
#                     # Create error message
#                     error_msg = ToolMessage(
#                         content=f"Error executing {tool_name}: {str(tool_error)}",
#                         tool_call_id=tool_call.get('id', 'unknown')
#                     )
#                     tool_messages.append(error_msg)
                    
#                     execution_log.append({
#                         'iteration': state['iterations'],
#                         'type': 'tool_execution',
#                         'tool': tool_name,
#                         'input': str(tool_call.get('args', {}))[:200],
#                         'success': False,
#                         'error': str(tool_error)
#                     })
            
#             return {
#                 "messages": tool_messages,
#                 "tools_used": tools_used,
#                 "execution_log": execution_log
#             }
        
#         def should_continue(state: AgentState) -> str:
#             """Decide whether to continue or end"""
#             last_message = state['messages'][-1]
            
#             # Check iteration limit
#             if state['iterations'] >= state['max_iterations']:
#                 return "end"
            
#             # Check if there are tool calls
#             if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
#                 return "continue"
            
#             # No more tool calls - end
#             return "end"
        
#         def finalize_answer(state: AgentState) -> AgentState:
#             """Extract final answer from conversation"""
#             last_message = state['messages'][-1]
            
#             if hasattr(last_message, 'content'):
#                 final_answer = last_message.content
#             else:
#                 final_answer = str(last_message)
            
#             return {
#                 "final_answer": final_answer
#             }
        
#         # Build LangGraph workflow
#         workflow = StateGraph(AgentState)
        
#         # Add nodes
#         workflow.add_node("agent", agent_node)
#         workflow.add_node("tools", tool_node)
#         workflow.add_node("finalize", finalize_answer)
        
#         # Add edges
#         workflow.set_entry_point("agent")
        
#         workflow.add_conditional_edges(
#             "agent",
#             should_continue,
#             {
#                 "continue": "tools",
#                 "end": "finalize"
#             }
#         )
        
#         workflow.add_edge("tools", "agent")
#         workflow.add_edge("finalize", END)
        
#         # Compile graph
#         app_graph = workflow.compile()
        
#         # Get user context
#         session = get_session(engine)
#         memory_mgr = MemoryManager(session)
#         user_context = memory_mgr.build_user_context(user_id, user_role)
        
#         # Initialize state
#         initial_state = {
#             "messages": [HumanMessage(content=f"{query_text}\n\nUser Context: {user_context}")],
#             "user_query": query_text,
#             "user_role": user_role,
#             "iterations": 0,
#             "max_iterations": max_iterations,
#             "final_answer": "",
#             "tools_used": [],
#             "execution_log": []
#         }
        
#         # Execute graph
#         logger.info(f"LangGraph agent executing query from user {user_id}: {query_text}")
        
#         try:
#             # Run the graph
#             final_state = app_graph.invoke(initial_state)
            
#             # Extract results
#             final_answer = final_state.get('final_answer', '')
#             tools_used = list(set(final_state.get('tools_used', [])))
#             iterations = final_state.get('iterations', 0)
#             execution_log = final_state.get('execution_log', [])
            
#             # Store query in database
#             try:
#                 new_query = Query(
#                     user_id=user_id,
#                     query_text=query_text,
#                     response_text=final_answer
#                 )
#                 session.add(new_query)
#                 session.commit()
#             except Exception as db_error:
#                 logger.error(f"Database error: {str(db_error)}")
            
#             # Build response
#             response_data = {
#                 'query': query_text,
#                 'response': final_answer,
#                 'agent_info': {
#                     'type': 'langgraph',
#                     'tools_available': tool_names,
#                     'tools_used': tools_used,
#                     'iterations': iterations,
#                     'max_iterations': max_iterations,
#                     'user_role': user_role
#                 },
#                 'execution_summary': f"LangGraph agent completed in {iterations} iterations using {len(tools_used)} tools out of {len(available_tools)} available"
#             }
            
#             # Add execution log if verbose
#             if verbose:
#                 response_data['execution_log'] = execution_log
            
#             logger.info(f"LangGraph agent completed: {len(tools_used)} tools used, {iterations} iterations")
            
#             return jsonify(response_data), 200
            
#         except Exception as graph_error:
#             logger.error(f"LangGraph execution error: {str(graph_error)}", exc_info=True)
            
#             # Fallback to basic reasoning engine
#             if reasoning_engine:
#                 session_db = get_session(engine)
#                 memory_mgr = MemoryManager(session_db)
#                 user_context = memory_mgr.build_user_context(user_id, user_role)
                
#                 fallback_response = reasoning_engine.generate_legal_advice(
#                     query_text,
#                     user_context,
#                     user_role
#                 )
#                 session_db.close()
                
#                 return jsonify({
#                     'query': query_text,
#                     'response': fallback_response,
#                     'warning': 'Agent execution failed, fallback response provided',
#                     'error_details': str(graph_error) if verbose else 'Enable verbose mode for details'
#                 }), 200
#             else:
#                 return jsonify({
#                     'error': 'Agent execution failed and no fallback available',
#                     'details': str(graph_error) if verbose else 'Enable verbose mode for details'
#                 }), 500
        
#     except Exception as e:
#         logger.error(f"Agent endpoint error: {str(e)}", exc_info=True)
#         return jsonify({
#             'error': f'An error occurred: {str(e)}',
#             'details': 'Please check server logs for more information'
#         }), 500
#     finally:
#         if session:
#             try:
#                 session.close()
#             except:
#                 pass

@app.route('/api/status', methods=['GET'])
def status_check():
    """Detailed status check endpoint"""
    status = {
        'database': 'unknown',
        'ai_modules': {
            'reasoning_engine': reasoning_engine is not None,
            # 'orchestrator': orchestrator is not None,
            'rag_tool': rag_tool is not None,
            'langchain_tools': langchain_tools is not None and len(langchain_tools) if langchain_tools else 0
        },
        'config': {
            'api_key_configured': bool(Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_gemini_api_key_here'),
            'upload_folder_exists': os.path.exists(Config.UPLOAD_FOLDER)
        }
    }
    
    # Add tool details if available
    if langchain_tools:
        status['tools'] = {
            'count': len(langchain_tools),
            'names': [tool.name for tool in langchain_tools],
            'descriptions': {tool.name: tool.description[:100] + '...' for tool in langchain_tools}
        }
    
    # Test database
    try:
        from sqlalchemy import text
        session = get_session(engine)
        session.execute(text('SELECT 1'))
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
    # Disable reloader on Python 3.13+ due to TensorFlow compatibility issues
    import sys
    use_reloader = app.config['DEBUG'] and sys.version_info < (3, 13)
    
    app.run(
        host='0.0.0.0',
        port=app.config['FLASK_PORT'],
        debug=app.config['DEBUG'],
        use_reloader=use_reloader
    )
