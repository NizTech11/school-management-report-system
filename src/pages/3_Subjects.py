import streamlit as st
from components.forms import subject_form

st.set_page_config(page_title="Subjects", page_icon="📚", layout="wide")

subject_form()
