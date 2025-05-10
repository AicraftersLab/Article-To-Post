"""
Configuration and initialization for the Article2Image Streamlit app.
"""
import logging
import openai
import streamlit as st
import google.generativeai as genai
import uuid

from src.api.gemini import configure_gemini
from src.api.openai_integration import configure_openai


def setup_logging():
    """Configure logging"""
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def configure_api_keys():
    """Configure the API keys from Streamlit secrets"""
    # Configure Google Generative AI
    gemini_configured = configure_gemini()
    
    # Configure OpenAI if API key is available (Optional)
    openai_client, openai_available = configure_openai()
    
    return gemini_configured, openai_client, openai_available


def set_page_config():
    """Set Streamlit page configuration"""
    st.set_page_config(
        page_title="Article2Image - Instagram Post Generator",
        page_icon="📰",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def get_custom_css():
    """Return the custom CSS for the app"""
    return """
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #1E88E5;
        }
        .stProgress > div > div > div > div {
            background-color: #1E88E5;
        }
        .stButton button {
            background-color: #1E88E5;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        .stButton button:hover {
            background-color: #1565C0;
            opacity: 0.9;
        }
        .highlight {
            background-color: #F5F7FA;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1.5rem 0;
            border-left: 5px solid #1E88E5;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .success-box {
            background-color: #E8F5E9;
            border-left: 5px solid #4CAF50;
            padding: 1rem;
            border-radius: 0 5px 5px 0;
            margin: 1rem 0;
        }
        .info-box {
            background-color: #E3F2FD;
            border-left: 5px solid #2196F3;
            padding: 1rem;
            border-radius: 0 5px 5px 0;
            margin: 1rem 0;
        }
        .warning-box {
            background-color: #FFF3E0;
            border-left: 5px solid #FF9800;
            padding: 1rem;
            border-radius: 0 5px 5px 0;
            margin: 1rem 0;
        }
        .step-counter {
            background-color: #1E88E5;
            color: white;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            text-align: center;
            line-height: 30px;
            margin-right: 10px;
            display: inline-block;
        }
        .preview-container {
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
        }
        /* Accessibility improvements */
        .stTextInput input, .stTextArea textarea {
            font-size: 16px !important;
            padding: 10px !important;
        }
        button {
            min-height: 44px !important; /* Ensure touch target size */
        }
        /* Focus indicators for accessibility */
        button:focus, input:focus, textarea:focus, select:focus {
            outline: 2px solid #1E88E5 !important;
            outline-offset: 2px !important;
        }
        /* High contrast form elements */
        .stTextInput input, .stTextArea textarea {
            border: 1px solid #555 !important;
        }
        /* Improved visual hierarchy */
        h1 {
            font-size: 32px !important;
            margin-bottom: 20px !important;
        }
        h2 {
            font-size: 24px !important;
            margin-top: 30px !important;
            margin-bottom: 15px !important;
        }
        h3 {
            font-size: 20px !important;
            margin-top: 25px !important;
            margin-bottom: 10px !important;
        }
    </style>
    """


def initialize_session_state():
    """Initialize the session state variables if they don't exist"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'image_style': 'photorealistic'
        }
        
    if 'language' not in st.session_state:
        st.session_state.language = 'fr'
        
    if 'page_id' not in st.session_state:
        st.session_state.page_id = str(uuid.uuid4())  # Create a unique session ID
        
    if 'image_generated' not in st.session_state:
        st.session_state.image_generated = False
        
    if 'generated' not in st.session_state:
        st.session_state.generated = False
        
    if 'article_text' not in st.session_state:
        st.session_state.article_text = ""


# Step navigation functions
def go_to_step(step_number):
    """Go to a specific step"""
    st.session_state.current_step = step_number
    st.rerun()
    
def next_step():
    """Go to the next step"""
    st.session_state.current_step += 1
    st.rerun()
    
def prev_step():
    """Go to the previous step"""
    if st.session_state.current_step > 1:
        st.session_state.current_step -= 1
        st.rerun() 