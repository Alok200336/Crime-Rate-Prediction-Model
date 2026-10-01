import streamlit as st
from components.api import get
from components.ui import header, inject_css, incident_card
st.set_page_config(page_title="Live Crime Feed", page_icon="📰", layout="wide"); inject_css(); header("📰 Live Crime Feed","Latest normalized crime reports collected by the ingestion pipeline")
meta=get("/meta/filters", default={"crime_types":[],"states":[]})
a,b,c=st.columns([2,1,1]); q=a.text_input("Search", placeholder="city, headline, keyword..."); ctype=b.selectbox("Crime type", [""]+meta.get("crime_types",[])); state=c.selectbox("State", [""]+meta.get("states",[]))
items=get("/incidents/search", {"q":q or None,"crime_type":ctype or None,"state":state or None,"limit":200}, [])
st.caption(f"{len(items)} matching reports")
for item in items: incident_card(item)
