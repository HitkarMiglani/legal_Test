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
from modules.embeddings import EmbeddingGenerator
from modules.legal_retriever import LegalRetriever
from modules.memory_manager import MemoryManager
from modules.orchestrator import LangChainOrchestrator
from modules.reasoning_engine import GeminiReasoningEngine

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])
CORS(app)

# Initialize database
engine = init_db(app.config['DATABASE_URL'])

# Initialize modules with error handling
doc_processor = DocumentProcessor(app.config['UPLOAD_FOLDER'])
embedding_gen = None
legal_retriever = LegalRetriever()
orchestrator = None
reasoning_engine = None

# Initialize AI modules with proper error handling
try:
    if Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_gemini_api_key_here':
        embedding_gen = EmbeddingGenerator()
        orchestrator = LangChainOrchestrator()
        reasoning_engine = GeminiReasoningEngine()
        print("✓ AI modules initialized successfully")
    else:
        print("⚠ Warning: GOOGLE_API_KEY not configured. AI features will be limited.")
        print("  Please set your API key in the .env file.")
except Exception as e:
    print(f"⚠ Warning: Failed to initialize AI modules: {str(e)}")
    print("  The application will run with limited functionality.")

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    """Analyze a document"""
    try:
        data = request.get_json()
        query = data.get('query', 'Provide a comprehensive analysis')
        analysis_type = data.get('type', 'comprehensive')
        
        user_id = request.current_user['user_id']
        user_role = request.current_user['role']
        
        session = get_session(engine)
        
        # Get document
        doc = session.query(Document).filter_by(id=doc_id, user_id=user_id).first()
        
        if not doc:
            session.close()
            return jsonify({'error': 'Document not found'}), 404
        
        # Check if AI modules are available
        if not reasoning_engine and not orchestrator:
            session.close()
            return jsonify({
                'error': 'AI service not available. Please configure GOOGLE_API_KEY in .env file and restart the server.'
            }), 503
        
        # Process document
        result = doc_processor.process_document(doc.file_path, doc.file_type)
        document_text = result['text']
        
        # Perform analysis
        try:
            if analysis_type == 'gemini' and reasoning_engine:
                analysis_result = reasoning_engine.analyze_legal_document(
                    document_text, 
                    analysis_type='comprehensive'
                )
                analysis = analysis_result.get('analysis', '')
            elif orchestrator:
                analysis = orchestrator.analyze_document(
                    document_text,
                    query,
                    user_role
                )
            else:
                analysis = "AI analysis service is currently unavailable. Please check your API configuration."
        except Exception as analysis_error:
            print(f"Analysis error: {str(analysis_error)}")
            analysis = f"Analysis failed: {str(analysis_error)}"
        
        session.close()
        
        return jsonify({
            'document_id': doc_id,
            'analysis': analysis
        }), 200
        
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
        
        # Step 3: Build context
        session = get_session(engine)
        memory_mgr = MemoryManager(session)
        user_context = memory_mgr.build_user_context(user_id, user_role)
        
        # Add case context
        if cases:
            user_context += "\n\nRelevant Cases:\n"
            for i, case in enumerate(cases[:3], 1):
                user_context += f"{i}. {case.get('title', 'N/A')}\n"
        
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
            'related_cases': cases[:3] if cases else []
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
            'embedding_gen': embedding_gen is not None,
            'api_key_configured': bool(Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_gemini_api_key_here')
        }
    }), 200

@app.route('/api/status', methods=['GET'])
def status_check():
    """Detailed status check endpoint"""
    status = {
        'database': 'unknown',
        'ai_modules': {
            'reasoning_engine': reasoning_engine is not None,
            'orchestrator': orchestrator is not None,
            'embedding_gen': embedding_gen is not None
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
        'message': 'Welcome to LuminaryAI API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/register, /api/auth/login',
            'documents': '/api/documents/upload, /api/documents',
            'query': '/api/query',
            'research': '/api/research/cases'
        }
    }), 200

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=app.config['FLASK_PORT'],
        debug=app.config['DEBUG']
    )
