import streamlit as st
from components import api

def render_sidebar():
    with st.sidebar:
        st.title('🛡️ Crime Intel India')
        st.caption('News-derived incident monitoring')
        try:
            status=api.health().get('status','unknown')
            st.success(f'Backend: {status}')
        except Exception:
            st.error('Backend unavailable')
        st.divider()
        st.caption('Important: records are derived from news reports and are not official NCRB crime statistics.')
