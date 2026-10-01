import streamlit as st
from components.api import get, post
from components.ui import header, inject_css
st.set_page_config(page_title="Pipeline Admin",page_icon="⚙️",layout="wide"); inject_css(); header("⚙️ Pipeline Admin","Development controls for ingestion and demo data")
st.warning("Protect this page before public deployment. The backend endpoint requires the ADMIN_API_KEY.")
st.json(get("/health",default={}))
a,b=st.columns(2)
if a.button("Run RSS ingestion",use_container_width=True):
    result=post("/ingestion/run"); st.success(result) if result else None
if b.button("Seed demo records",use_container_width=True):
    result=post("/ingestion/seed-demo"); st.success(result) if result else None

st.sidebar.text_input("Admin API key", type="password", key="admin_key")
