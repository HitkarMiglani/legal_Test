"""
Streamlit Frontend for LuminaryAI
"""
import os
import warnings

# Suppress gRPC and other warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
warnings.filterwarnings('ignore')

import streamlit as st
import requests
from datetime import datetime

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')

# Page configuration
st.set_page_config(
    page_title="LuminaryAI - Legal Intelligence Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E3A8A;
        color: white;
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1E40AF;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        padding: 1rem;
        background-color: #D1FAE5;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #10B981;
    }
    .error-box {
        padding: 1rem;
        background-color: #FEE2E2;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #EF4444;
    }
    .info-box {
        padding: 1rem;
        background-color: #DBEAFE;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #3B82F6;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .status-online { background-color: #10B981; }
    .status-offline { background-color: #EF4444; }
    .feature-card {
        padding: 1.5rem;
        border-radius: 0.75rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
    }
    .assistant-message {
        background-color: #F3F4F6;
        border-left: 4px solid #10B981;
    }
    [data-testid="stSidebar"] {
        background-color: #F9FAFB;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent_chat_history' not in st.session_state:
    st.session_state.agent_chat_history = []
if 'api_connected' not in st.session_state:
    st.session_state.api_connected = None

# Helper functions
def check_api_connection():
    """Check if API is connected"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        st.session_state.api_connected = response.status_code == 200
        return st.session_state.api_connected
    except:
        st.session_state.api_connected = False
        return False

def make_api_request(endpoint, method='GET', data=None, files=None, timeout=30):
    """Make API request with authentication and error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if st.session_state.token:
        headers['Authorization'] = f"Bearer {st.session_state.token}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == 'POST':
            if files:
                response = requests.post(url, headers=headers, files=files, data=data, timeout=timeout)
            else:
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout)
        
        return response
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The server is taking too long to respond.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection error. Please check if the backend server is running.")
        st.session_state.api_connected = False
        return None
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

def login_page():
    """Login/Register page"""
    st.markdown('<div class="main-header">⚖️ LuminaryAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Agentic Legal Intelligence Assistant for Indian Law</div>', unsafe_allow_html=True)
    
    # Check API connection
    api_status = check_api_connection()
    if not api_status:
        st.error("🔴 **Backend API is not connected.** Please ensure the Flask backend is running on http://localhost:5000")
        st.info("💡 Start the backend with: `python app.py`")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("🔐 Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("🔐 Login", use_container_width=True)
            
            if submit:
                if username and password:
                    with st.spinner("Logging in..."):
                        response = make_api_request('/auth/login', 'POST', {
                            'username': username,
                            'password': password
                        })
                        
                        if response and response.status_code == 200:
                            data = response.json()
                            st.session_state.token = data['token']
                            st.session_state.user = data['user']
                            st.success("✅ Login successful!")
                            st.rerun()
                        elif response and response.status_code == 401:
                            st.error("❌ Invalid username or password. Please try again.")
                        else:
                            error_msg = "Login failed"
                            if response:
                                try:
                                    error_data = response.json()
                                    error_msg = error_data.get('error', error_msg)
                                except:
                                    error_msg = f"Server returned status {response.status_code}"
                            st.error(f"❌ {error_msg}")
                else:
                    st.error("⚠️ Please fill all fields")
    
    with tab2:
        st.subheader("📝 Create New Account")
        st.caption("Join LuminaryAI to access intelligent legal assistance")
        
        with st.form("register_form"):
            reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
            reg_email = st.text_input("Email", key="reg_email", placeholder="your.email@example.com")
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Create a strong password", help="Use at least 8 characters")
            reg_role = st.selectbox(
                "I am a...", 
                ["public", "student", "lawyer"],
                help="Select your role to get personalized responses"
            )
            reg_submit = st.form_submit_button("📝 Register", use_container_width=True)
            
            if reg_submit:
                if reg_username and reg_email and reg_password:
                    # Basic validation
                    if len(reg_password) < 8:
                        st.error("⚠️ Password must be at least 8 characters long")
                    elif '@' not in reg_email:
                        st.error("⚠️ Please enter a valid email address")
                    else:
                        with st.spinner("Creating account..."):
                            response = make_api_request('/auth/register', 'POST', {
                                'username': reg_username,
                                'email': reg_email,
                                'password': reg_password,
                                'role': reg_role
                            })
                            
                            if response and response.status_code == 201:
                                data = response.json()
                                st.session_state.token = data['token']
                                st.session_state.user = data['user']
                                st.success("✅ Registration successful! Welcome to LuminaryAI!")
                                st.rerun()
                            elif response and response.status_code == 400:
                                error_data = response.json()
                                error_msg = error_data.get('error', 'Registration failed')
                                st.error(f"❌ {error_msg}")
                            else:
                                error_msg = "Registration failed"
                                if response:
                                    try:
                                        error_data = response.json()
                                        error_msg = error_data.get('error', error_msg)
                                    except:
                                        error_msg = f"Server returned status {response.status_code}"
                                st.error(f"❌ {error_msg}")
                else:
                    st.error("⚠️ Please fill all required fields")

def main_app():
    """Main application interface"""
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user['username']}!")
        st.markdown(f"**Role:** {st.session_state.user['role'].title()}")
        
        st.divider()
        
        # API Connection Status
        api_status = check_api_connection()
        status_color = "🟢 Online" if api_status else "🔴 Offline"
        st.caption(f"API Status: {status_color}")
        
        st.divider()
        
        page = st.radio("Navigation", [
            "🏠 Home",
            "📄 Document Analysis",
            "💬 Legal Assistant",
            "🤖 Agent Query",
            "📚 Document RAG",
            "🔍 Legal Research",
            "📁 My Documents"
        ])
        
        st.divider()
        
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.chat_history = []
            st.rerun()
    
    # Main content
    if page == "🏠 Home":
        show_home_page()
    elif page == "📄 Document Analysis":
        show_document_analysis()
    elif page == "💬 Legal Assistant":
        show_legal_assistant()
    elif page == "🤖 Agent Query":
        show_agent_query()
    elif page == "📚 Document RAG":
        show_document_rag()
    elif page == "🔍 Legal Research":
        show_legal_research()
    elif page == "📁 My Documents":
        show_my_documents()

def show_home_page():
    """Home page"""
    st.markdown('<div class="main-header">⚖️ LuminaryAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Making Indian law understandable, accessible, and intelligent</div>', unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='padding: 1.5rem; border-radius: 0.75rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin-bottom: 1rem;'>
            <h3>📄 Document Analysis</h3>
            <p>Upload and analyze legal documents with AI-powered insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='padding: 1.5rem; border-radius: 0.75rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; margin-bottom: 1rem;'>
            <h3>💬 Legal Assistant</h3>
            <p>Get answers to your legal questions in simple language</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='padding: 1.5rem; border-radius: 0.75rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; margin-bottom: 1rem;'>
            <h3>🤖 Agent Query</h3>
            <p>Autonomous AI agent manages documents and performs complex operations</p>
        </div>
        """, unsafe_allow_html=True)
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.markdown("### 📚 Document RAG")
        st.write("Manage your document knowledge base - search, query, and organize documents")
    
    with col5:
        st.markdown("### 🔍 Legal Research")
        st.write("Search Indian case law and legal precedents")
    
    st.divider()
    
    st.markdown("### 🌟 Key Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        - ✅ **Agentic Legal Intelligence** (LangChain + Gemini)
        - ✅ **Document Analysis** (PDF/DOCX/TXT)
        - ✅ **Role-Based Personalization** (Lawyer/Student/Public)
        - ✅ **Autonomous Document Management** (9 AI tools)
        """)
    
    with feature_col2:
        st.markdown("""
        - ✅ **Real-Time Legal Intelligence** (Indian Kanoon API)
        - ✅ **Semantic Search & Matching** (RAG Pipeline)
        - ✅ **Personalized Memory** (Context-aware)
        - ✅ **Secure & Private** (JWT + Encryption)
        """)
    
    st.divider()
    
    st.warning("⚠️ **Disclaimer:** LuminaryAI provides AI-generated summaries of Indian laws and legal documents for educational and informational purposes only. It is not a substitute for professional legal advice.")

def show_document_analysis():
    """Document analysis page"""
    st.markdown("## 📄 Document Analysis")
    st.caption("Upload and analyze legal documents with AI-powered insights")
    
    uploaded_file = st.file_uploader(
        "Upload a legal document (PDF, DOCX, or TXT)",
        type=['pdf', 'docx', 'txt'],
        help="Maximum file size: 10MB"
    )
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        with st.form("analysis_form"):
            analysis_query = st.text_area(
                "What would you like to know about this document?",
                placeholder="E.g., Summarize the key points, Identify potential risks, etc.",
                value="Provide a comprehensive analysis of this legal document"
            )
            
            analysis_type = st.selectbox(
                "Analysis Type",
                ["comprehensive", "summary", "specific", "gemini"]
            )
            
            analyze_button = st.form_submit_button("Analyze Document")
            
            if analyze_button:
                with st.spinner("Uploading and processing document..."):
                    # Upload document
                    files = {'file': uploaded_file}
                    response = make_api_request('/documents/upload', 'POST', files=files)
                    
                    if response and response.status_code == 200:
                        doc_data = response.json()
                        doc_id = doc_data['document_id']
                        
                        st.success("Document uploaded successfully!")
                        
                        # Analyze document
                        with st.spinner("Analyzing document..."):
                            analysis_response = make_api_request(
                                f'/documents/{doc_id}/analyze',
                                'POST',
                                {
                                    'query': analysis_query,
                                    'type': analysis_type
                                }
                            )
                            
                            if analysis_response and analysis_response.status_code == 200:
                                analysis_data = analysis_response.json()
                                
                                st.markdown("### ✅ Analysis Results")
                                st.markdown(analysis_data['analysis'])
                                
                                # Show metadata if available
                                if analysis_data.get('metadata'):
                                    with st.expander("📊 Document Metadata"):
                                        st.json(analysis_data['metadata'])
                                
                                # Show key elements if available
                                if analysis_data.get('key_elements'):
                                    with st.expander("🔑 Key Elements"):
                                        st.json(analysis_data['key_elements'])
                                
                                # Option to add to RAG
                                st.divider()
                                if st.button("➕ Add to RAG Knowledge Base", use_container_width=True):
                                    # Extract text and add to RAG
                                    doc_text_response = make_api_request(f'/documents/{doc_id}', 'GET')
                                    if doc_text_response and doc_text_response.status_code == 200:
                                        doc_data = doc_text_response.json()
                                        # Note: This endpoint may not exist, but we'll try
                                        st.info("Note: To add to RAG, use the Document RAG page after uploading.")
                            else:
                                error_msg = "Analysis failed"
                                if analysis_response:
                                    try:
                                        error_data = analysis_response.json()
                                        error_msg = error_data.get('error', error_msg)
                                    except:
                                        error_msg = f"Server returned status {analysis_response.status_code}"
                                st.error(f"❌ {error_msg}")
                                if st.button("🔄 Retry Analysis", key="retry_analysis"):
                                    st.rerun()
                    else:
                        error_msg = "Upload failed"
                        if response:
                            try:
                                error_data = response.json()
                                error_msg = error_data.get('error', error_msg)
                            except:
                                error_msg = f"Server returned status {response.status_code}"
                        st.error(f"❌ {error_msg}")
                        if st.button("🔄 Retry Upload", key="retry_upload"):
                            st.rerun()

def show_legal_assistant():
    """Legal assistant chat page"""
    st.markdown("## 💬 Legal Assistant")
    st.caption("Ask questions about Indian law and get AI-powered responses")
    
    # Response mode selector and clear button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        response_mode = st.selectbox(
            "Response Type",
            ["Short & Concise", "Detailed"],
            key="response_mode",
            help="Choose concise for quick answers or detailed for comprehensive explanations"
        )
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            st.rerun()
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Display chat history
    if not st.session_state.chat_history:
        st.info("👋 Start a conversation! Ask me anything about Indian law.")
    
    for idx, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show validation info if available
            if message.get("validation"):
                with st.expander("📊 Query Analysis"):
                    val = message["validation"]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        score = val.get('quality_score', 'N/A')
                        color = "normal" if isinstance(score, (int, float)) and score >= 7 else "inverse"
                        st.metric("Quality Score", f"{score}/10", delta=None if score == 'N/A' else None)
                    with col2:
                        st.metric("Domain", val.get('legal_domain', 'N/A').title())
                    with col3:
                        st.metric("Clarity", val.get('is_clear', 'N/A').upper())
            
            # Show related documents if available
            if message.get("related_documents"):
                with st.expander("📄 Related Documents"):
                    for doc in message["related_documents"]:
                        st.markdown(f"**{doc.get('title', 'Document')}**")
                        st.caption(f"Relevance: {doc.get('relevance', 0):.2%}")
                        if doc.get('preview'):
                            st.caption(doc['preview'][:150] + "...")
                        st.divider()
    
    # Chat input
    if prompt := st.chat_input("Ask a legal question..."):
        # Validate minimum length
        if len(prompt.strip()) < 10:
            st.error("⚠️ Please provide a more detailed question (at least 10 characters)")
            return
        
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your question and generating response..."):
                mode = 'short' if response_mode == "Short & Concise" else 'detailed'
                response = make_api_request('/query', 'POST', {
                    'query': prompt,
                    'mode': mode
                })
                
                if response and response.status_code == 200:
                    data = response.json()
                    assistant_response = data['response']
                    
                    # Show query reiteration notice if applicable
                    if data.get('query_reiterated'):
                        st.info(f"🔄 **Query Enhanced**: Your question was clarified for better results\n\n"
                               f"Original: *{data.get('original_query')}*\n\n"
                               f"Enhanced: *{data.get('query')}*")
                    
                    # Show response mode indicator
                    if data.get('mode') == 'short':
                        st.info("📝 **Concise Answer** (Request detailed mode for more information)")
                    
                    st.markdown(assistant_response)
                    
                    # Show validation info
                    if data.get('validation'):
                        with st.expander("📊 Query Analysis"):
                            val = data['validation']
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                score = val.get('quality_score', 'N/A')
                                st.metric("Quality Score", f"{score}/10")
                            with col2:
                                domain = val.get('legal_domain', 'general')
                                st.metric("Legal Domain", domain.title())
                            with col3:
                                clarity = val.get('is_clear', 'yes')
                                st.metric("Query Clarity", clarity.upper())
                            
                            # Show suggestions if score was low
                            if val.get('suggestions'):
                                st.info(f"💡 **Tip**: {val['suggestions']}")
                    
                    # Show related cases if available
                    if data.get('related_cases'):
                        with st.expander("⚖️ Related Legal Cases"):
                            for case in data['related_cases']:
                                st.markdown(f"**{case.get('title', 'N/A')}**")
                                st.caption(f"Court: {case.get('court', 'N/A')} | Date: {case.get('date', 'N/A')}")
                                if case.get('summary'):
                                    st.markdown(case.get('summary'))
                                st.divider()
                    
                    # Show related documents if available
                    if data.get('related_documents'):
                        with st.expander("📄 Related Documents from Knowledge Base"):
                            for doc in data['related_documents']:
                                st.markdown(f"**{doc.get('title', 'Document')}**")
                                st.caption(f"Relevance: {doc.get('relevance', 0):.2%}")
                                if doc.get('preview'):
                                    st.caption(doc['preview'][:200] + "...")
                                st.divider()
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": assistant_response,
                        "validation": data.get('validation'),
                        "related_documents": data.get('related_documents', [])
                    })
                    
                elif response and response.status_code == 400:
                    # Validation failed
                    error_data = response.json()
                    st.error(f"❌ {error_data.get('error', 'Invalid query')}")
                    
                    if error_data.get('suggestions'):
                        st.info(f"💡 **Suggestion:** {error_data['suggestions']}")
                    
                    if error_data.get('validation'):
                        with st.expander("See validation details"):
                            st.json(error_data['validation'])
                else:
                    error_msg = "Failed to get response."
                    if response:
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('error', error_msg)
                        except:
                            error_msg = f"Server returned status {response.status_code}"
                    
                    st.error(f"❌ {error_msg}")
                    if st.button("🔄 Retry", key=f"retry_{len(st.session_state.chat_history)}"):
                        st.rerun()

def show_legal_research():
    """Legal research page"""
    st.markdown("## 🔍 Legal Research")
    st.caption("Search Indian case law and legal precedents")
    
    search_query = st.text_input(
        "Search for cases, laws, or legal concepts",
        placeholder="e.g., contract breach, property rights, IPC Section 420"
    )
    limit = st.number_input("Number of results", min_value=1, max_value=20, value=10)
    
    if st.button("🔍 Search", use_container_width=True) and search_query:
        with st.spinner("Searching case law..."):
            response = make_api_request(f'/research/cases?q={search_query}&limit={limit}', 'GET')
            
            if response and response.status_code == 200:
                data = response.json()
                cases = data.get('cases', [])
                
                if cases:
                    st.success(f"Found {len(cases)} results")
                    
                    for idx, case in enumerate(cases, 1):
                        with st.expander(f"{idx}. {case.get('title', 'Unknown Case')}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**Court:** {case.get('court', 'N/A')}")
                                st.markdown(f"**Date:** {case.get('date', 'N/A')}")
                            
                            with col2:
                                st.markdown(f"**Citation:** {case.get('citation', 'N/A')}")
                                if case.get('case_id'):
                                    st.caption(f"ID: {case['case_id']}")
                            
                            if case.get('summary'):
                                st.divider()
                                st.markdown("**Summary:**")
                                st.markdown(case['summary'])
                            
                            if case.get('keywords'):
                                st.divider()
                                st.caption(f"**Keywords:** {', '.join(case.get('keywords', []))}")
                else:
                    st.info("No cases found. Try a different search term or check if the Indian Kanoon API is configured.")
            else:
                error_msg = "Search failed"
                if response:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', error_msg)
                    except:
                        error_msg = f"Server returned status {response.status_code}"
                st.error(f"❌ {error_msg}")

def show_agent_query():
    """Autonomous agent query page"""
    st.markdown("## 🤖 Agent Query")
    st.caption("Use the autonomous AI agent to manage documents and perform complex multi-step operations")
    
    # Info box
    st.info("💡 **Tip**: The agent can autonomously add documents, search, compare, and analyze. "
            "Just describe what you want in natural language!")
    
    # Clear history button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Clear History", key="clear_agent_history"):
            st.session_state.agent_chat_history = []
            st.success("Agent history cleared!")
            st.rerun()
    
    # Display agent chat history
    if not st.session_state.agent_chat_history:
        st.info("👋 Ask the agent to perform document operations! Example: 'Add this contract and find all termination clauses'")
    
    for message in st.session_state.agent_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tools_used"):
                st.caption(f"🔧 Tools used: {message['tools_used']}")
            if message.get("timestamp"):
                st.caption(f"⏰ {message['timestamp']}")
    
    # Agent query input
    if prompt := st.chat_input("Tell the agent what to do...", key="agent_input"):
        if len(prompt.strip()) < 10:
            st.error("⚠️ Please provide a more detailed instruction (at least 10 characters)")
            return
        
        # Add user message
        st.session_state.agent_chat_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Agent is thinking and executing tools..."):
                response = make_api_request('/agent/query', 'POST', {
                    'query': prompt,
                    'verbose': False
                }, timeout=120)
                
                if response and response.status_code == 200:
                    data = response.json()
                    agent_response = data.get('answer', 'No response from agent')
                    
                    st.markdown(agent_response)
                    
                    if data.get('tools_available'):
                        st.caption(f"🔧 {data['tools_available']} tools available to agent")
                    
                    st.session_state.agent_chat_history.append({
                        "role": "assistant",
                        "content": agent_response,
                        "tools_used": data.get('tools_available'),
                        "timestamp": data.get('timestamp', datetime.now().isoformat())
                    })
                    
                elif response and response.status_code == 503:
                    st.error("❌ Agent service not available. Please configure GOOGLE_API_KEY and ensure the backend is running.")
                else:
                    error_msg = "Agent execution failed."
                    if response:
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('error', error_msg)
                        except:
                            error_msg = f"Server returned status {response.status_code}"
                    
                    st.error(f"❌ {error_msg}")
                    if st.button("🔄 Retry", key=f"retry_agent_{len(st.session_state.agent_chat_history)}"):
                        st.rerun()

def show_document_rag():
    """Document RAG management page"""
    st.markdown("## 📚 Document RAG Management")
    st.caption("Manage your document knowledge base - add, search, and query documents")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Add Document", "🔍 Search Documents", "💬 Query Document", "🔄 Compare Documents", "📋 List Documents"])
    
    with tab1:
        st.markdown("### Add Document to RAG")
        st.caption("Add documents to your knowledge base for semantic search and Q&A")
        
        with st.form("add_rag_document"):
            doc_content = st.text_area(
                "Document Content",
                placeholder="Paste or type the document content here...",
                height=200
            )
            doc_title = st.text_input("Document Title", placeholder="e.g., Rental Agreement 2025")
            doc_metadata = st.text_input(
                "Metadata (JSON format, optional)",
                placeholder='{"type": "contract", "date": "2025-01-15"}',
                help="Optional JSON metadata for the document"
            )
            
            submit = st.form_submit_button("➕ Add to RAG", use_container_width=True)
            
            if submit:
                if doc_content and doc_title:
                    import json
                    metadata = {}
                    if doc_metadata:
                        try:
                            metadata = json.loads(doc_metadata)
                        except:
                            st.warning("⚠️ Invalid JSON metadata. Continuing without metadata.")
                    
                    with st.spinner("Adding document to RAG..."):
                        response = make_api_request('/rag/documents', 'POST', {
                            'content': doc_content,
                            'title': doc_title,
                            'metadata': metadata
                        })
                        
                        if response and response.status_code == 200:
                            data = response.json()
                            st.success(f"✅ Document added successfully!")
                            st.info(f"**Document ID:** `{data.get('doc_id', 'N/A')}`\n"
                                   f"**Chunks created:** {data.get('chunks_created', 0)}")
                        else:
                            st.error("Failed to add document to RAG")
                else:
                    st.error("Please provide both document content and title")
    
    with tab2:
        st.markdown("### Search Documents")
        st.caption("Semantic search across all documents in your knowledge base")
        
        search_query = st.text_input("Search Query", placeholder="e.g., termination clauses, notice period")
        top_k = st.number_input("Number of Results", min_value=1, max_value=20, value=5)
        
        if st.button("🔍 Search", use_container_width=True) and search_query:
            with st.spinner("Searching documents..."):
                response = make_api_request('/rag/search', 'POST', {
                    'query': search_query,
                    'top_k': top_k
                })
                
                if response and response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    if results:
                        st.success(f"Found {len(results)} relevant results")
                        for idx, result in enumerate(results, 1):
                            with st.expander(f"{idx}. {result.get('doc_title', 'Document')} (Similarity: {result.get('similarity', 0):.2%})"):
                                st.markdown(f"**Document:** {result.get('doc_title', 'N/A')}")
                                st.markdown(f"**Similarity:** {result.get('similarity', 0):.4f}")
                                st.markdown("**Relevant Text:**")
                                st.code(result.get('text', '')[:500] + "..." if len(result.get('text', '')) > 500 else result.get('text', ''))
                    else:
                        st.info("No results found. Try a different search query.")
                else:
                    st.error("Search failed")
    
    with tab3:
        st.markdown("### Query Specific Document")
        st.caption("Ask questions about a specific document in your knowledge base")
        
        # First, get list of documents
        list_response = make_api_request('/rag/documents', 'GET')
        doc_options = {}
        
        if list_response and list_response.status_code == 200:
            docs = list_response.json().get('documents', [])
            if docs:
                doc_options = {f"{doc['title']} ({doc['doc_id']})": doc['doc_id'] for doc in docs}
        
        if doc_options:
            selected_doc = st.selectbox("Select Document", list(doc_options.keys()))
            doc_id = doc_options[selected_doc]
            
            question = st.text_area("Your Question", placeholder="e.g., What is the notice period?")
            
            if st.button("❓ Ask Question", use_container_width=True) and question:
                with st.spinner("Querying document..."):
                    response = make_api_request(f'/rag/documents/{doc_id}/query', 'POST', {
                        'question': question
                    })
                    
                    if response and response.status_code == 200:
                        data = response.json()
                        st.success("✅ Answer Generated")
                        st.markdown("**Answer:**")
                        st.markdown(data.get('answer', 'No answer generated'))
                        
                        if data.get('sources'):
                            with st.expander(f"📄 Sources ({len(data['sources'])} chunks used)"):
                                for idx, source in enumerate(data['sources'], 1):
                                    st.markdown(f"**Source {idx}** (Similarity: {source.get('similarity', 0):.4f})")
                                    st.caption(source.get('text', '')[:200] + "...")
                                    st.divider()
                    else:
                        st.error("Failed to query document")
        else:
            st.info("No documents in RAG yet. Add documents in the 'Add Document' tab first.")
    
    with tab4:
        st.markdown("### Compare Two Documents")
        st.caption("Compare two documents and identify differences, similarities, and key points")
        
        # Get list of documents
        list_response = make_api_request('/rag/documents', 'GET')
        doc_options = {}
        
        if list_response and list_response.status_code == 200:
            docs = list_response.json().get('documents', [])
            if docs and len(docs) >= 2:
                doc_options = {f"{doc['title']} ({doc['doc_id']})": doc['doc_id'] for doc in docs}
        
        if doc_options and len(doc_options) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                selected_doc1 = st.selectbox("Select First Document", list(doc_options.keys()), key="compare_doc1")
                doc_id1 = doc_options[selected_doc1]
            
            with col2:
                # Filter out doc1 from options
                doc2_options = {k: v for k, v in doc_options.items() if v != doc_id1}
                if doc2_options:
                    selected_doc2 = st.selectbox("Select Second Document", list(doc2_options.keys()), key="compare_doc2")
                    doc_id2 = doc2_options[selected_doc2]
                else:
                    st.warning("Please select a different document for comparison")
                    doc_id2 = None
            
            if doc_id1 and doc_id2 and doc_id1 != doc_id2:
                if st.button("🔄 Compare Documents", use_container_width=True):
                    with st.spinner("Comparing documents..."):
                        response = make_api_request('/rag/documents/compare', 'POST', {
                            'doc_id1': doc_id1,
                            'doc_id2': doc_id2
                        })
                        
                        if response and response.status_code == 200:
                            data = response.json()
                            st.success("✅ Comparison Complete")
                            
                            if data.get('comparison'):
                                st.markdown("### Comparison Results")
                                st.markdown(data['comparison'])
                            
                            if data.get('similarities'):
                                with st.expander("🔗 Similarities"):
                                    st.markdown(data['similarities'])
                            
                            if data.get('differences'):
                                with st.expander("⚡ Differences"):
                                    st.markdown(data['differences'])
                        else:
                            st.error("Failed to compare documents")
        elif doc_options and len(doc_options) < 2:
            st.warning("⚠️ You need at least 2 documents in RAG to compare. Add more documents first.")
        else:
            st.info("No documents in RAG yet. Add at least 2 documents to enable comparison.")
    
    with tab5:
        st.markdown("### All Documents in RAG")
        
        if st.button("🔄 Refresh List", use_container_width=True):
            st.rerun()
        
        with st.spinner("Loading documents..."):
            response = make_api_request('/rag/documents', 'GET')
            
            if response and response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                
                if documents:
                    st.success(f"Found {len(documents)} documents in RAG")
                    
                    for doc in documents:
                        with st.expander(f"📄 {doc.get('title', 'Untitled')} ({doc.get('doc_id', 'N/A')})"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Words", doc.get('words', 0))
                            with col2:
                                st.metric("Chunks", doc.get('chunks', 0))
                            with col3:
                                st.metric("Added", doc.get('added_at', 'N/A')[:10] if doc.get('added_at') else 'N/A')
                            
                            if doc.get('metadata'):
                                st.json(doc['metadata'])
                            
                            # Delete button
                            if st.button(f"🗑️ Delete", key=f"delete_{doc.get('doc_id')}", use_container_width=True):
                                delete_response = make_api_request(f"/rag/documents/{doc.get('doc_id')}", 'DELETE')
                                if delete_response and delete_response.status_code == 200:
                                    st.success("Document deleted!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete document")
                else:
                    st.info("No documents in RAG yet. Add your first document in the 'Add Document' tab!")
            else:
                st.error("Failed to load documents")

def show_my_documents():
    """My documents page"""
    st.markdown("## 📁 My Uploaded Documents")
    st.caption("Documents you've uploaded to the system")
    
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    
    response = make_api_request('/documents', 'GET')
    
    if response and response.status_code == 200:
        data = response.json()
        documents = data.get('documents', [])
        
        if documents:
            st.success(f"Found {len(documents)} documents")
            
            for doc in documents:
                with st.expander(f"📄 {doc['filename']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Type:** {doc['file_type'].upper()}")
                        st.markdown(f"**Uploaded:** {doc['uploaded_at'][:19] if len(doc.get('uploaded_at', '')) > 19 else doc['uploaded_at']}")
                    
                    with col2:
                        status_color = {
                            'completed': '🟢',
                            'processing': '🟡',
                            'pending': '⚪',
                            'failed': '🔴'
                        }
                        status_emoji = status_color.get(doc['processed'], '⚪')
                        st.markdown(f"**Status:** {status_emoji} {doc['processed'].title()}")
                    
                    with col3:
                        if doc['processed'] == 'completed':
                            if st.button("📊 Analyze", key=f"analyze_{doc['id']}", use_container_width=True):
                                st.session_state.selected_doc_id = doc['id']
                                st.session_state.show_analysis = True
                                st.rerun()
        else:
            st.info("No documents uploaded yet. Go to Document Analysis to upload your first document!")
    else:
        st.error("Failed to load documents")

# Main app logic
def main():
    """Main entry point"""
    if st.session_state.token is None:
        login_page()
    else:
        main_app()

if __name__ == '__main__':
    main()
