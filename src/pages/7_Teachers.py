import streamlit as st
from components.teachers import teacher_form, display_teachers, teacher_statistics, password_reset_form

st.set_page_config(page_title="Teachers", page_icon="👨‍🏫", layout="wide")

st.title("👨‍🏫 Teacher Management")

# Create tabs for different teacher operations
tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Teacher", "👥 View Teachers", "� Reset Password", "�📊 Statistics"])

with tab1:
    st.header("Add New Teacher")
    teacher_form()

with tab2:
    st.header("All Teachers")
    display_teachers()

with tab3:
    st.header("Password Reset")
    password_reset_form()

with tab4:
    teacher_statistics()
