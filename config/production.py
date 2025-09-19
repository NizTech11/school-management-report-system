"""
Production Configuration for Streamlit School Management System
"""
import streamlit as st
import os

# Production Streamlit Configuration
def configure_production():
    """Configure Streamlit for production deployment"""
    
    # Page configuration
    st.set_page_config(
        page_title="School Management System",
        page_icon="🏫",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://your-school-website.com/support',
            'Report a bug': 'https://your-school-website.com/contact',
            'About': """
            # School Management System v2.0
            
            A comprehensive solution for managing student records, marks, and reports.
            
            **Features:**
            - Multi-user support with role-based access
            - Real-time grade calculations
            - Bulk PDF report generation
            - Secure data management
            
            Contact your system administrator for support.
            """
        }
    )
    
    # Hide Streamlit branding in production
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Add custom CSS for better mobile experience
    mobile_css = """
    <style>
    @media (max-width: 768px) {
        .stSidebar {
            width: 100% !important;
        }
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    </style>
    """
    st.markdown(mobile_css, unsafe_allow_html=True)

# Environment-specific settings
PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

if PRODUCTION:
    configure_production()