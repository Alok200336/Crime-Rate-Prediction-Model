import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")


def get(path: str, params=None, default=None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=10)
        r.raise_for_status(); return r.json()
    except requests.RequestException as exc:
        st.error(f"Backend API unavailable: {exc}")
        return default if default is not None else []


def post(path: str, data=None):
    key = st.session_state.get("admin_key", ADMIN_API_KEY)
    if not key:
        st.error("Enter your admin key in the sidebar."); return None
    try:
        r = requests.post(f"{API_BASE}{path}", json=data, headers={"X-Admin-Key": key}, timeout=60)
        r.raise_for_status(); return r.json()
    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}"); return None
