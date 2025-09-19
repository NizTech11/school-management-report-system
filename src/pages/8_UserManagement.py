import streamlit as st
from components.auth import create_user_management_interface
from utils.rbac import require_permission

st.set_page_config(page_title="User Management", page_icon="👥", layout="wide")

@require_permission("system.users")
def render_user_management():
    create_user_management_interface()

render_user_management()