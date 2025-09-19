"""
Advanced Reporting System Page
Main page for accessing the comprehensive reporting features
"""

import streamlit as st
from utils.rbac import has_permission, get_current_user, require_permission
from components.reports import render_reports_management

# Page configuration
st.set_page_config(
    page_title="Advanced Reports - Student Management System",
    page_icon="📊",
    layout="wide"
)

def main():
    """Main function for the reports page"""
    
    # Check if user is authenticated
    current_user = get_current_user()
    if not current_user:
        st.error("Please log in to access the reporting system.")
        st.stop()
    
    # Check basic reporting permissions
    if not has_permission(current_user['role'], "reports.templates.view"):
        st.error("You don't have permission to access the reporting system.")
        st.info("Contact your administrator to request reporting access.")
        st.stop()
    
    # Render the reports management interface
    render_reports_management()

if __name__ == "__main__":
    main()