import streamlit as st
from components.classes import class_form, display_classes, class_statistics

st.set_page_config(page_title="Classes", page_icon="🏫", layout="wide")

st.title("🏫 Class Management")

# Create tabs for different class management functions
tab1, tab2, tab3 = st.tabs(["Add Classes", "View Classes", "Statistics"])

with tab1:
    class_form()

with tab2:
    display_classes()

with tab3:
    class_statistics()
