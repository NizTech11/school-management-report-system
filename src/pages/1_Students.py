import streamlit as st
from components.forms import student_form, display_students

st.set_page_config(page_title="Students", page_icon="🎓", layout="wide")

st.title("🎓 Student Management")

# Create tabs for different student operations
tab1, tab2 = st.tabs(["➕ Add Student", "👥 View All Students"])

with tab1:
    st.header("Add New Student")
    student_form()

with tab2:
    display_students()
