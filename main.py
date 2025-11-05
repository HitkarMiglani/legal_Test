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

st.session_state["dark_mode"] = False
# Dynamic CSS based on theme
def get_theme_colors():
    """Get color scheme based on dark mode setting"""
    
    if st.session_state.dark_mode:
        return {
            'bg_primary': '#0F172A',
            'bg_secondary': '#1E293B',
            'bg_tertiary': '#334155',
            'text_primary': '#F1F5F9',
            'text_secondary': '#CBD5E1',
            'text_muted': '#94A3B8',
            'accent_primary': '#8B5CF6',
            'accent_secondary': '#EC4899',
            'accent_tertiary': '#06B6D4',
            'success': '#10B981',
            'error': '#EF4444',
            'warning': '#F59E0B',
            'border': '#475569',
            'shadow': 'rgba(0, 0, 0, 0.5)',
            'gradient_1': 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
            'gradient_2': 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)',
            'gradient_3': 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            'hero_gradient': 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 50%, #F97316 100%)',
            'hover':'#334155',
        }
    else:
        return {
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F8FAFC',
            'bg_tertiary': '#F1F5F9',
            'text_primary': '#0F172A',
            'text_secondary': '#334155',
            'text_muted': '#64748B',
            'accent_primary': '#8B5CF6',
            'accent_secondary': '#EC4899',
            'accent_tertiary': '#06B6D4',
            'success': '#10B981',
            'error': '#EF4444',
            'warning': '#F59E0B',
            'border': '#E2E8F0',
            'shadow': 'rgba(0, 0, 0, 0.1)',
            'gradient_1': 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
            'gradient_2': 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)',
            'gradient_3': 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
            'hero_gradient': 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 50%, #F97316 100%)',
            'hover':'#E2E8F0',
        }

colors = get_theme_colors()

# Custom CSS - Enhanced with Dark Mode Support
st.markdown(f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {{
        font-family: 'Inter', sans-serif;
        transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
    }}
    
    /* Main Background */
    .main {{
        background-color: {colors['bg_primary']};
        color: {colors['text_primary']};
    }}
    
    /* Sections Background */
    section[data-testid="stSidebar"],
    .stApp {{
        background-color: {colors['bg_primary']};
        color: {colors['text_primary']};
    }}
    
    .main-header {{
        font-family: 'Outfit', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: {colors['hero_gradient']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        animation: gradient-shift 8s ease infinite;
        background-size: 200% 200%;
    }}
    
    @keyframes gradient-shift {{
        0%, 100% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
    }}
    
    .sub-header {{
        font-size: 1.3rem;
        color: {colors['text_secondary']};
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
        line-height: 1.6;
    }}
    
    .hero-section {{
        background: {colors['gradient_1']};
        padding: 4rem 2rem;
        border-radius: 1.5rem;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 25px 70px {colors['shadow']};
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .hero-section::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        animation: pulse-hero 15s ease-in-out infinite;
    }}
    
    .hero-section::after {{
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 100%;
        height: 100px;
        background: linear-gradient(to top, rgba(0,0,0,0.1), transparent);
    }}
    
    @keyframes pulse-hero {{
        0%, 100% {{ transform: scale(1) rotate(0deg); opacity: 0.5; }}
        50% {{ transform: scale(1.2) rotate(180deg); opacity: 0.8; }}
    }}
    
    .hero-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
        letter-spacing: -0.02em;
    }}
    
    .hero-subtitle {{
        font-size: 1.5rem;
        opacity: 0.95;
        margin-bottom: 2rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}
    
    .stButton>button {{
        width: 100%;
        background: {colors['gradient_1']};
        color: white;
        border: none;
        border-radius: 1rem;
        padding: 0.875rem 1.75rem;
        font-weight: 700;
        font-size: 1.05rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
        letter-spacing: 0.025em;
        position: relative;
        overflow: hidden;
    }}
    
    .stButton>button::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }}
    
    .stButton>button:hover {{
        background: {colors['gradient_2']};
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 32px rgba(139, 92, 246, 0.5);
    }}
    
    .stButton>button:hover::before {{
        width: 300px;
        height: 300px;
    }}
    
    .stButton>button:active {{
        transform: translateY(-1px) scale(0.98);
    }}
    
    .feature-card {{
        padding: 2.5rem;
        border-radius: 1.25rem;
        background: {colors['bg_secondary']};
        border: 2px solid {colors['border']};
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }}
    
    .feature-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: {colors['gradient_1']};
        opacity: 0;
        transition: opacity 0.4s ease;
        z-index: 0;
    }}
    
    .feature-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 50px {colors['shadow']};
        border-color: {colors['accent_primary']};
    }}
    
    .feature-card:hover::before {{
        opacity: 0.1;
    }}
    
    .feature-icon {{
        font-size: 3.5rem;
        margin-bottom: 1.25rem;
        display: block;
        position: relative;
        z-index: 1;
        filter: drop-shadow(0 4px 8px {colors['shadow']});
    }}
    
    .feature-title {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {colors['text_primary']};
        margin-bottom: 0.875rem;
        position: relative;
        z-index: 1;
        font-family: 'Outfit', sans-serif;
    }}
    
    .feature-description {{
        color: {colors['text_secondary']};
        font-size: 1.05rem;
        line-height: 1.7;
        position: relative;
        z-index: 1;
    }}
    
    .stat-card {{
        background: {colors['bg_secondary']};
        padding: 2rem;
        border-radius: 1.25rem;
        box-shadow: 0 8px 24px {colors['shadow']};
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid {colors['border']};
        position: relative;
        overflow: hidden;
    }}
    
    .stat-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: {colors['gradient_1']};
    }}
    
    .stat-card:hover {{
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 12px 35px {colors['shadow']};
        border-color: {colors['accent_primary']};
    }}
    
    .stat-number {{
        font-size: 3rem;
        font-weight: 800;
        background: {colors['gradient_1']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        font-family: 'Outfit', sans-serif;
    }}
    
    .stat-label {{
        color: {colors['text_secondary']};
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .success-box {{
        padding: 1.25rem;
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        border-radius: 0.75rem;
        margin: 1rem 0;
        border-left: 4px solid #10B981;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15);
    }}
    
    .error-box {{
        padding: 1.5rem;
        background: {colors['bg_secondary']};
        border-radius: 1rem;
        margin: 1rem 0;
        border-left: 5px solid {colors['error']};
        box-shadow: 0 4px 12px {colors['shadow']};
        border: 1px solid {colors['border']};
    }}
    
    .info-box {{
        padding: 1.5rem;
        background: {colors['bg_secondary']};
        border-radius: 1rem;
        margin: 1rem 0;
        border-left: 5px solid {colors['accent_tertiary']};
        box-shadow: 0 4px 12px {colors['shadow']};
        border: 1px solid {colors['border']};
    }}
    
    .chat-message {{
        padding: 1.5rem;
        border-radius: 1.25rem;
        margin: 0.875rem 0;
        box-shadow: 0 4px 12px {colors['shadow']};
        transition: all 0.3s ease;
        border: 1px solid {colors['border']};
    }}
    
    .chat-message:hover {{
        box-shadow: 0 8px 20px {colors['shadow']};
        transform: translateX(5px);
    }}
    
    .user-message {{
        background: {colors['bg_secondary']};
        border-left: 5px solid {colors['accent_tertiary']};
    }}
    
    .assistant-message {{
        background: {colors['bg_secondary']};
        border-left: 5px solid {colors['success']};
    }}
    
    [data-testid="stSidebar"] {{
        background: {colors['bg_secondary']};
        border-right: 2px solid {colors['border']};
    }}
    
    [data-testid="stSidebar"] .stRadio > label {{
        font-weight: 600;
        color: {colors['text_primary']};
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }}
    
    .sidebar-user-info {{
        background: {colors['gradient_1']};
        padding: 2rem;
        border-radius: 1.25rem;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }}
    
    .sidebar-user-info::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate-gradient 10s linear infinite;
    }}
    
    @keyframes rotate-gradient {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    
    .status-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.625rem 1.25rem;
        border-radius: 2rem;
        font-size: 0.9rem;
        font-weight: 600;
        gap: 0.625rem;
        box-shadow: 0 2px 8px {colors['shadow']};
    }}
    
    .status-online {{
        background: {colors['gradient_3']};
        color: white;
    }}
    
    .status-offline {{
        background: linear-gradient(135deg, {colors['error']} 0%, #DC2626 100%);
        color: white;
    }}
    
    .status-dot {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        animation: pulse-dot 2s ease-in-out infinite;
        box-shadow: 0 0 10px currentColor;
    }}
    
    .status-dot.online {{
        background-color: white;
    }}
    
    .status-dot.offline {{
        background-color: white;
    }}
    
    @keyframes pulse-dot {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.6; transform: scale(1.2); }}
    }}
    
    /* Card with gradient border */
    .gradient-border-card {{
        position: relative;
        padding: 2.5rem;
        border-radius: 1.25rem;
        background: {colors['bg_secondary']};
        margin: 1rem 0;
        border: 2px solid {colors['border']};
    }}
    
    .gradient-border-card::before {{
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 1.25rem;
        padding: 2px;
        background: {colors['gradient_1']};
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1rem;
        background-color: {colors['bg_tertiary']};
        padding: 0.75rem;
        border-radius: 1rem;
        border: 1px solid {colors['border']};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 0.75rem;
        font-weight: 600;
        padding: 0.875rem 1.75rem;
        color: {colors['text_secondary']};
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {colors['gradient_1']};
        color: white;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }}
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea {{
        border-radius: 1rem;
        border: 2px solid {colors['border']};
        background-color: {colors['bg_secondary']};
        color: {colors['text_primary']};
        transition: all 0.3s ease;
        padding: 0.875rem 1.25rem;
    }}
    
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {colors['accent_primary']};
        box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.2);
        background-color: {colors['bg_primary']};
    }}
    
    /* Dark Mode Toggle Button */
    .dark-mode-toggle {{
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        z-index: 9999;
        background: {colors['gradient_1']};
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 1.5rem;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .dark-mode-toggle:hover {{
        transform: scale(1.1) rotate(15deg);
        box-shadow: 0 12px 32px rgba(139, 92, 246, 0.5);
    }}
    
    .dark-mode-toggle:active {{
        transform: scale(0.95) rotate(0deg);
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
        
    /* Expander */
    .streamlit-expanderHeader {{
        border-radius: 0.75rem;
        font-weight: 500;
        transition: all 0.2s ease;
        background: {colors['bg_secondary']};
        border: 1px solid {colors['border']};
        }}
    
    .streamlit-expanderHeader:hover {{
        background: {colors['hover']};
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {colors['text_primary']};
        font-weight: 700;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {colors['text_secondary']};
        font-weight: 500;
    }}
    
    /* Info/Alert boxes */
    .stAlert {{
        background: {colors['bg_secondary']};
        border-left: 4px solid {colors['accent_primary']};
        border-radius: 0.75rem;
        padding: 1rem;
    }}
    
    /* Dataframes and Tables */
    [data-testid="stDataFrame"] {{
        border: 1px solid {colors['border']};
        border-radius: 0.75rem;
        overflow: hidden;
    }}
    
    .stTable {{
        background: {colors['bg_secondary']};
        border-radius: 0.75rem;
    }}
    
    /* Code blocks */
    .stCodeBlock {{
        background: {colors['bg_secondary']};
        border: 1px solid {colors['border']};
        border-radius: 0.75rem;
    }}
    
    /* Chat Messages */
    .chat-message {{
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding: 1.25rem;
        border-radius: 1rem;
        animation: slideIn 0.3s ease-out;
    }}
    
    @keyframes slideIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .user-message {{
        background: {colors['gradient_1']};
        color: white;
        margin-left: 2rem;
    }}
    
    .assistant-message {{
        background: {colors['bg_secondary']};
        border: 1px solid {colors['border']};
        margin-right: 2rem;
    }}
    
    .message-icon {{
        font-size: 1.75rem;
        min-width: 2.5rem;
        height: 2.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
    }}
    
    .message-content {{
        flex: 1;
        line-height: 1.6;
        font-size: 1rem;
    }}
    
    .user-message .message-content {{
        color: white;
    }}
    
    .assistant-message .message-content {{
        color: {colors['text_primary']};
    }}
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
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

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
        # Dark mode toggle
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            mode_icon = "🌙" if not st.session_state.dark_mode else "☀️"
            mode_text = "Dark Mode" if not st.session_state.dark_mode else "Light Mode"
            if st.button(f"{mode_icon} {mode_text}", use_container_width=True, key="theme_toggle"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        
        st.divider()
        
        # User info card
        st.markdown(f"""
        <div class="sidebar-user-info">
            <div style="font-size: 2.5rem; text-align: center; margin-bottom: 0.5rem;">👤</div>
            <div style="font-size: 1.25rem; font-weight: 600; text-align: center; margin-bottom: 0.25rem;">
                {st.session_state.user['username']}
            </div>
            <div style="text-align: center; opacity: 0.9; font-size: 0.9rem;">
                {st.session_state.user['role'].title()} Account
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # API Connection Status
        api_status = check_api_connection()
        status_class = "online" if api_status else "offline"
        status_text = "Online" if api_status else "Offline"
        st.markdown(f"""
        <div class="status-badge status-{status_class}">
            <span class="status-dot {status_class}"></span>
            API Status: {status_text}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        page = st.radio("📍 Navigation", [
            "🏠 Home",
            "📄 Document Analysis",
            "💬 Legal Assistant",
            "🤖 Agent Query",
            "📚 Document RAG",
            "🔍 Legal Research",
            "📁 My Documents"
        ], label_visibility="visible")
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.chat_history = []
            page = "🏠 Home"
            # st.rerun()
    
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

def show_landing_page():
    """Landing page for non-authenticated users"""
    
    # Hero Section with Get Started Button
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">⚖️ LuminaryAI</div>
        <div class="hero-subtitle">
            Your Intelligent Legal Companion for Indian Law
        </div>
        <p style="font-size: 1.1rem; opacity: 0.9; max-width: 800px; margin: 0 auto; position: relative; z-index: 1; margin-bottom: 2rem;">
            Empowering legal professionals, students, and citizens with AI-driven document analysis, 
            autonomous agents, and comprehensive legal intelligence.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get Started Button - Centered
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Get Started", key="landing_get_started", use_container_width=True, type="primary"):
            st.session_state.show_login = True
            st.rerun()
    
    # Quick Stats
    st.markdown("### 📊 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">10+</div>
            <div class="stat-label">AI Tools</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">3</div>
            <div class="stat-label">User Roles</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">∞</div>
            <div class="stat-label">Documents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Features
    st.markdown("### ✨ Core Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📄</span>
            <div class="feature-title">Document Analysis</div>
            <div class="feature-description">
                Upload and analyze legal documents with AI-powered insights. 
                Supports PDF, DOCX, and TXT formats with comprehensive analysis capabilities.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">💬</span>
            <div class="feature-title">Legal Assistant</div>
            <div class="feature-description">
                Get instant answers to legal questions with role-based responses 
                tailored for lawyers, students, or the general public.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">Autonomous Agent</div>
            <div class="feature-description">
                Intelligent agent with 10+ tools that autonomously manages documents, 
                performs searches, and executes complex operations.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📚</span>
            <div class="feature-title">Document RAG</div>
            <div class="feature-description">
                Semantic search and Q&A across your document knowledge base 
                with advanced retrieval-augmented generation.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🔍</span>
            <div class="feature-title">Legal Research</div>
            <div class="feature-description">
                Search Indian case law and legal precedents with 
                real-time access to comprehensive legal databases.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📁</span>
            <div class="feature-title">Document Manager</div>
            <div class="feature-description">
                Organize, track, and manage all your uploaded documents 
                in one secure, centralized location.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Technology Stack
    st.markdown("### 🚀 Powered By")
    
    tech_col1, tech_col2 = st.columns(2)
    
    with tech_col1:
        st.markdown("""
        <div class="gradient-border-card">
            <h4 style="color: #1E3A8A; margin-bottom: 1rem;">🧠 AI & Intelligence</h4>
            <ul style="color: #64748B; line-height: 2;">
                <li><strong>LangGraph</strong> - State-based agent workflows</li>
                <li><strong>Google Gemini</strong> - Advanced language model</li>
                <li><strong>LangChain</strong> - Agent orchestration framework</li>
                <li><strong>ChromaDB</strong> - Vector database for RAG</li>
                <li><strong>Sentence Transformers</strong> - Semantic embeddings</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_col2:
        st.markdown("""
        <div class="gradient-border-card">
            <h4 style="color: #1E3A8A; margin-bottom: 1rem;">🛠️ Infrastructure</h4>
            <ul style="color: #64748B; line-height: 2;">
                <li><strong>Flask</strong> - Backend REST API</li>
                <li><strong>Streamlit</strong> - Interactive frontend</li>
                <li><strong>SQLAlchemy</strong> - Database ORM</li>
                <li><strong>JWT</strong> - Secure authentication</li>
                <li><strong>Indian Kanoon API</strong> - Legal database</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # How It Works
    st.markdown("### 💡 How It Works")
    
    step_col1, step_col2, step_col3, step_col4 = st.columns(4)
    
    with step_col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">1️⃣</div>
            <h4 style="color: #1E3A8A; margin-bottom: 0.5rem;">Upload</h4>
            <p style="color: #64748B; font-size: 0.9rem;">
                Add legal documents or ask questions
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with step_col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">2️⃣</div>
            <h4 style="color: #1E3A8A; margin-bottom: 0.5rem;">Process</h4>
            <p style="color: #64748B; font-size: 0.9rem;">
                AI analyzes and indexes content
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with step_col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">3️⃣</div>
            <h4 style="color: #1E3A8A; margin-bottom: 0.5rem;">Execute</h4>
            <p style="color: #64748B; font-size: 0.9rem;">
                Agent selects and uses appropriate tools
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with step_col4:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">4️⃣</div>
            <h4 style="color: #1E3A8A; margin-bottom: 0.5rem;">Deliver</h4>
            <p style="color: #64748B; font-size: 0.9rem;">
                Get comprehensive, sourced answers
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Start
    st.markdown("### 🎯 Quick Start Guide")
    
    quick_col1, quick_col2 = st.columns(2)
    
    with quick_col1:
        st.info("""
        **👥 For Legal Professionals:**
        1. Use **Document Analysis** for contract review
        2. Leverage **Agent Query** for multi-document operations
        3. Access **Legal Research** for case law
        4. Get detailed, technical responses
        """)
    
    with quick_col2:
        st.info("""
        **📚 For Students & Public:**
        1. Ask questions in **Legal Assistant**
        2. Upload study materials to **Document RAG**
        3. Get simplified, educational responses
        4. Learn about Indian law concepts
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("""
    <div style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); 
                padding: 2rem; border-radius: 1rem; text-align: center; 
                border: 2px solid #BFDBFE; margin: 2rem 0;">
        <h3 style="color: #1E3A8A; margin-bottom: 1rem;">Ready to Get Started?</h3>
        <p style="color: #64748B; font-size: 1.1rem; margin-bottom: 1.5rem;">
            Choose a feature from the sidebar to begin your legal intelligence journey
        </p>
        <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
            <span style="background: white; padding: 0.75rem 1.5rem; border-radius: 2rem; 
                         color: #1E3A8A; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                🤖 10+ AI Tools
            </span>
            <span style="background: white; padding: 0.75rem 1.5rem; border-radius: 2rem; 
                         color: #1E3A8A; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                🔒 Secure & Private
            </span>
            <span style="background: white; padding: 0.75rem 1.5rem; border-radius: 2rem; 
                         color: #1E3A8A; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                ⚡ Real-time Results
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer
    st.warning("⚠️ **Important Disclaimer:** LuminaryAI provides AI-generated legal information for educational and informational purposes only. This is not a substitute for professional legal advice. Always consult with a qualified legal professional for specific legal matters.")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #94A3B8; font-size: 0.9rem; margin-top: 2rem;">
        <p>Made with ❤️ for the Indian Legal Community</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">
            Powered by LangGraph • Google Gemini • LangChain • ChromaDB
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_home_page():
    """Authenticated home page - shown in sidebar navigation when logged in"""
    st.markdown('<div class="main-header">⚖️ LuminaryAI Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Welcome back, {st.session_state.user["username"]}! 👋</div>', unsafe_allow_html=True)
    
    # Quick Stats
    st.markdown("### 📊 Your Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">10+</div>
            <div class="stat-label">AI Tools Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">∞</div>
            <div class="stat-label">Documents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="font-size: 1.8rem;">{st.session_state.user['role'].title()}</div>
            <div class="stat-label">Your Role</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Features
    st.markdown("### ✨ Quick Access")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📄</span>
            <div class="feature-title">Document Analysis</div>
            <div class="feature-description">
                Upload and analyze legal documents with AI-powered insights
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">💬</span>
            <div class="feature-title">Legal Assistant</div>
            <div class="feature-description">
                Get instant answers to your legal questions
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">Autonomous Agent</div>
            <div class="feature-description">
                Let AI manage documents and perform complex operations
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Start for authenticated users
    st.markdown("### 🎯 Quick Start Guide")
    
    role = st.session_state.user['role']
    
    if role == 'lawyer':
        st.info("""
        **👨‍⚖️ Recommended Workflow for Legal Professionals:**
        1. Upload contracts in **Document Analysis** for detailed review
        2. Use **Agent Query** for multi-document comparison and analysis
        3. Access **Legal Research** for relevant case law and precedents
        4. Get technical, detailed responses with legal citations
        """)
    elif role == 'student':
        st.info("""
        **📚 Recommended Workflow for Law Students:**
        1. Ask conceptual questions in **Legal Assistant**
        2. Upload study materials to **Document RAG** for easy reference
        3. Use **Legal Research** to find relevant cases
        4. Get clear, educational explanations with examples
        """)
    else:
        st.info("""
        **👤 Recommended Workflow:**
        1. Start with **Legal Assistant** for simple questions
        2. Upload documents to **Document Analysis** for review
        3. Use **Document RAG** to build your knowledge base
        4. Get simplified, accessible answers in plain language
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("""
    <div style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); 
                padding: 2rem; border-radius: 1rem; text-align: center; 
                border: 2px solid #BFDBFE; margin: 2rem 0;">
        <h3 style="color: #1E3A8A; margin-bottom: 1rem;">Ready to Begin?</h3>
        <p style="color: #64748B; font-size: 1.1rem; margin-bottom: 1.5rem;">
            Choose a feature from the sidebar to start using LuminaryAI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer
    st.warning("⚠️ **Important Disclaimer:** LuminaryAI provides AI-generated legal information for educational purposes only. This is not a substitute for professional legal advice.")

def show_document_analysis():
    """Document analysis page"""
    st.markdown("## 📄 Document Analysis")
    st.caption("Upload and analyze legal documents with AI-powered insights")
    
    # Create tabs for different modes
    tab1, tab2 = st.tabs(["📤 Upload New Document", "💬 Chat with Previous Documents"])
    
    with tab1:
        show_upload_and_analyze()
    
    with tab2:
        show_chat_with_documents()

def show_upload_and_analyze():
    """Upload and analyze new document"""
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
                        print(doc_data)
                        doc_id = doc_data['document_id']
                        
                        
                        st.success("Document uploaded successfully!")
                        
                        # Analyze document
                        with st.spinner("Analyzing document..."):
                            print("DOC_ID:",doc_id)
                            analysis_response = make_api_request(
                                f'/documents/{doc_id}/analyze',
                                'POST',
                                {
                                    'query': analysis_query,
                                    'type': analysis_type,
                                    'doc_id': doc_id
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
                                # st.divider()
                                # if st.button("➕ Add to RAG Knowledge Base", use_container_width=True):
                                    # Extract text and add to RAG
                                    # doc_text_response = make_api_request(f'/documents/{doc_id}', 'GET')
                                    # if doc_text_response and doc_text_response.status_code == 200:
                                    #     doc_data = doc_text_response.json()
                                    #     # Note: This endpoint may not exist, but we'll try
                                    #     st.info("Note: To add to RAG, use the Document RAG page after uploading.")
                            else:
                                error_msg = "Analysis failed"
                                if analysis_response:
                                    try:
                                        error_data = analysis_response.json()
                                        error_msg = error_data.get('error', error_msg)
                                    except:
                                        error_msg = f"Server returned status {analysis_response.status_code}"
                                st.error(f"❌ {error_msg}")
                    else:
                        error_msg = "Upload failed"
                        if response:
                            try:
                                error_data = response.json()
                                error_msg = error_data.get('error', error_msg)
                            except:
                                error_msg = f"Server returned status {response.status_code}"
                        st.error(f"❌ {error_msg}")

def show_chat_with_documents():
    """Chat with previously uploaded documents using RAG"""
    st.markdown("### 💬 Chat with Your Documents")
    st.caption("Select a document and ask questions about it")
    
    # Fetch RAG documents
    with st.spinner("Loading your documents..."):
        response = make_api_request('/documents', 'GET')
    
    if response and response.status_code == 200 :
        rag_data = response.json()
        documents = rag_data.get('documents', [])
        
        if not documents:
            st.info("📭 No documents found in your RAG knowledge base. Upload documents from the 'Document RAG' page first.")
            return
        
        # print(documents)
        # Document selector
        doc_options = {f"{doc['filename']} (ID: {doc['doc_id'][:8]}...)": doc['doc_id'] 
                      for doc in documents}
        
        selected_doc_label = st.selectbox(
            "Select a document to chat with:",
            options=list(doc_options.keys()),
            help="Choose a document from your RAG knowledge base"
        )
        
        selected_doc_id = doc_options[selected_doc_label]
        
        # Show document info
        selected_doc = next(doc for doc in documents if doc['doc_id'] == selected_doc_id)
        
        with st.expander("📄 Document Details", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Title:** {selected_doc['filename']}")
                st.markdown(f"**ID:** `{selected_doc['doc_id'][:16]}...`")
            with col2:
                if selected_doc.get('metadata'):
                    st.markdown(f"**Added:** {selected_doc['metadata'].get('added_at', 'N/A')}")
        
        st.divider()
        
        # Initialize chat history for this document
        chat_key = f"doc_chat_{selected_doc_id}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for i, msg in enumerate(st.session_state[chat_key]):
                if msg['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-icon">👤</div>
                        <div class="message-content">{msg['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-icon">🤖</div>
                        <div class="message-content">{msg['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([5, 1])
        with col1:
            user_question = st.text_input(
                "Ask a question about this document:",
                placeholder="E.g., What are the main points? What are the obligations mentioned?",
                key=f"question_input_{selected_doc_id}",
                label_visibility="collapsed"
            )
        with col2:
            send_button = st.button("Send 📤", use_container_width=True, key=f"send_{selected_doc_id}")
        
        # Clear chat button
        if st.session_state[chat_key]:
            if st.button("🗑️ Clear Chat", key=f"clear_{selected_doc_id}"):
                st.session_state[chat_key] = []
                st.rerun()
        
        # Process question
        if send_button and user_question:
            # Add user message
            st.session_state[chat_key].append({
                'role': 'user',
                'content': user_question
            })
            
            with st.spinner("🔍 Searching document and generating answer..."):
                # Query the document
                print("Selected Doc_ID:",selected_doc_id)
                query_response = make_api_request(
                    f'/documents/{selected_doc_id}/analyze',
                    'POST',
                    {'query': user_question}
                )
                print(query_response)
                
                if query_response and query_response.status_code == 200:
                    answer_data = query_response.json()
                    answer = answer_data.get('analysis', 'No answer generated')
                    
                    # Add assistant message
                    st.session_state[chat_key].append({
                        'role': 'assistant',
                        'content': answer
                    })
                    
                    # Show relevant chunks if available
                    if answer_data.get('chunks'):
                        with st.expander("📚 Relevant Document Sections", expanded=False):
                            for idx, chunk in enumerate(answer_data['chunks'][:3], 1):
                                st.markdown(f"**Section {idx}:**")
                                st.text(chunk['text'][:300] + "..." if len(chunk['text']) > 300 else chunk['text'])
                                st.markdown("---")
                    
                    st.rerun()
                else:
                    error_msg = "Failed to get answer"
                    if query_response:
                        try:
                            error_data = query_response.json()
                            error_msg = error_data.get('error', error_msg)
                        except:
                            error_msg = f"Server returned status {query_response.status_code}"
                    
                    st.session_state[chat_key].append({
                        'role': 'assistant',
                        'content': f"❌ Error: {error_msg}"
                    })
                    st.rerun()
    
    else:
        st.error("❌ Failed to load documents. Please check your connection.")

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
    # If user is logged in, show main app
    if st.session_state.token is not None:
        main_app()
    # If show_login flag is set, show login page
    elif st.session_state.show_login:
        login_page()
    # Otherwise show landing page
    else:
        show_landing_page()

if __name__ == '__main__':
    main()
