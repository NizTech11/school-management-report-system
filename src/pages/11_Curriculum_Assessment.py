import streamlit as st
from utils.rbac import get_current_user, has_permission
from components.curriculum import render_curriculum_management

st.set_page_config(page_title="Curriculum & Assessment", page_icon="📚", layout="wide")

def main():
    # Get current user
    user = get_current_user()
    if not user:
        st.error("Please log in to access this page")
        return
    
    # Check permissions for curriculum management
    if not has_permission(user['role'], 'curriculum.manage'):
        st.error("You don't have permission to manage curriculum & assessment")
        st.info("Contact your administrator for access")
        return
    
    # Render the curriculum management interface
    render_curriculum_management()


if __name__ == "__main__":
    main()