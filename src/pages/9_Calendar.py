import streamlit as st
from components.calendar import render_academic_calendar
from utils.rbac import require_permission, get_current_user

st.set_page_config(page_title="Academic Calendar", page_icon="📅", layout="wide")

def render_calendar_page():
    """Render the academic calendar page with role-based access"""
    user = get_current_user()
    if not user:
        st.error("Please log in to access this feature.")
        return
    
    # Check if user has calendar access
    if user['role'] not in ['Teacher', 'Head', 'Admin']:
        st.error("You don't have permission to access the calendar.")
        return
    
    render_academic_calendar()

render_calendar_page()