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
    }
    .success-box {
        padding: 1rem;
        background-color: #D1FAE5;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #FEE2E2;
        border-radius: 0.5rem;
        margin: 1rem 0;
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

# Helper functions
def make_api_request(endpoint, method='GET', data=None, files=None):
    """Make API request with authentication"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if st.session_state.token:
        headers['Authorization'] = f"Bearer {st.session_state.token}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            if files:
                response = requests.post(url, headers=headers, files=files, data=data)
            else:
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=data)
        
        return response
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def login_page():
    """Login/Register page"""
    st.markdown('<div class="main-header">⚖️ LuminaryAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Agentic Legal Intelligence Assistant for Indian Law</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    response = make_api_request('/auth/login', 'POST', {
                        'username': username,
                        'password': password
                    })
                    
                    if response and response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data['token']
                        st.session_state.user = data['user']
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.error("Please fill all fields")
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            reg_username = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_role = st.selectbox("I am a...", ["public", "student", "lawyer"])
            reg_submit = st.form_submit_button("Register")
            
            if reg_submit:
                if reg_username and reg_email and reg_password:
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
                        st.success("Registration successful!")
                        st.rerun()
                    else:
                        st.error("Registration failed")
                else:
                    st.error("Please fill all fields")

def main_app():
    """Main application interface"""
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user['username']}!")
        st.markdown(f"**Role:** {st.session_state.user['role'].title()}")
        
        st.divider()
        
        page = st.radio("Navigation", [
            "🏠 Home",
            "📄 Document Analysis",
            "💬 Legal Assistant",
            "🔍 Legal Research",
            "📚 My Documents"
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
    elif page == "🔍 Legal Research":
        show_legal_research()
    elif page == "📚 My Documents":
        show_my_documents()

def show_home_page():
    """Home page"""
    st.markdown('<div class="main-header">⚖️ LuminaryAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Making Indian law understandable, accessible, and intelligent</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📄 Document Analysis")
        st.write("Upload and analyze legal documents with AI-powered insights")
    
    with col2:
        st.markdown("### 💬 Legal Assistant")
        st.write("Get answers to your legal questions in simple language")
    
    with col3:
        st.markdown("### 🔍 Legal Research")
        st.write("Search Indian case law and legal precedents")
    
    st.divider()
    
    st.markdown("### 🌟 Key Features")
    
    features = [
        "✅ Agentic Legal Intelligence (LangChain + Gemini)",
        "✅ Document Analysis (PDF/DOCX/TXT)",
        "✅ Role-Based Personalization",
        "✅ Real-Time Legal Intelligence",
        "✅ Semantic Search & Matching",
        "✅ Personalized Memory",
        "✅ Secure & Private"
    ]
    
    for feature in features:
        st.markdown(feature)
    
    st.divider()
    
    st.warning("⚠️ **Disclaimer:** LuminaryAI provides AI-generated summaries of Indian laws and legal documents for educational and informational purposes only. It is not a substitute for professional legal advice.")

def show_document_analysis():
    """Document analysis page"""
    st.markdown("## 📄 Document Analysis")
    
    uploaded_file = st.file_uploader(
        "Upload a legal document (PDF, DOCX, or TXT)",
        type=['pdf', 'docx', 'txt']
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
                                
                                st.markdown("### Analysis Results")
                                st.markdown(analysis_data['analysis'])
                            else:
                                st.error("Analysis failed")
                    else:
                        st.error("Upload failed")

def show_legal_assistant():
    """Legal assistant chat page"""
    st.markdown("## 💬 Legal Assistant")
    
    # Response mode selector
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Ask me anything about Indian law!")
    with col2:
        response_mode = st.selectbox(
            "Response Type",
            ["Short & Concise", "Detailed"],
            key="response_mode"
        )
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show validation info if available
            if message.get("validation"):
                with st.expander("📊 Query Analysis"):
                    val = message["validation"]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Quality Score", f"{val.get('quality_score', 'N/A')}/10")
                    with col2:
                        st.metric("Domain", val.get('legal_domain', 'N/A').title())
                    with col3:
                        st.metric("Clarity", val.get('is_clear', 'N/A').upper())
    
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
                                st.markdown(case.get('summary', ''))
                                st.divider()
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": assistant_response,
                        "validation": data.get('validation')
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
                    st.error("Failed to get response. Please try again.")

def show_legal_research():
    """Legal research page"""
    st.markdown("## 🔍 Legal Research")
    
    search_query = st.text_input("Search for cases, laws, or legal concepts")
    
    if st.button("Search") and search_query:
        with st.spinner("Searching..."):
            response = make_api_request(f'/research/cases?q={search_query}&limit=10', 'GET')
            
            if response and response.status_code == 200:
                data = response.json()
                cases = data.get('cases', [])
                
                if cases:
                    st.success(f"Found {len(cases)} results")
                    
                    for case in cases:
                        with st.expander(f"{case.get('title', 'Unknown Case')}"):
                            st.markdown(f"**Court:** {case.get('court', 'N/A')}")
                            st.markdown(f"**Date:** {case.get('date', 'N/A')}")
                            st.markdown(f"**Citation:** {case.get('citation', 'N/A')}")
                            
                            if case.get('summary'):
                                st.markdown("**Summary:**")
                                st.markdown(case['summary'])
                else:
                    st.info("No cases found. Try a different search term.")
            else:
                st.error("Search failed")

def show_my_documents():
    """My documents page"""
    st.markdown("## 📚 My Documents")
    
    response = make_api_request('/documents', 'GET')
    
    if response and response.status_code == 200:
        data = response.json()
        documents = data.get('documents', [])
        
        if documents:
            for doc in documents:
                with st.expander(f"📄 {doc['filename']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Type:** {doc['file_type'].upper()}")
                        st.markdown(f"**Uploaded:** {doc['uploaded_at']}")
                    
                    with col2:
                        status_color = {
                            'completed': '🟢',
                            'processing': '🟡',
                            'pending': '⚪',
                            'failed': '🔴'
                        }
                        st.markdown(f"**Status:** {status_color.get(doc['processed'], '⚪')} {doc['processed'].title()}")
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
