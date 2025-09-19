import streamlit as st
from components.forms import marks_form

st.set_page_config(page_title="Marks", page_icon="📝", layout="wide")

marks_form()
