import pandas as pd
import streamlit as st
from components.api import get
from components.ui import header, inject_css, incident_card

st.set_page_config(page_title="Crime Intelligence India", page_icon="🛡️", layout="wide")
inject_css(); header("🛡️ Crime Intelligence India", "News-derived crime monitoring, trends and geographic intelligence across India")
st.caption("Coverage reflects collected news reports, not official crime statistics. Verify incidents using the original source and official records.")

stats = get("/analytics/stats", default={})
cols = st.columns(5)
for col, label, key in zip(cols,["Total incidents","Added today","States covered","News sources","Top category"],["total_incidents","incidents_today","states_covered","sources_covered","top_crime_type"]):
    col.metric(label, stats.get(key, 0) or "—")

left,right = st.columns([1.05,1.6])
with left:
    st.subheader("🔥 Trending categories")
    trending = get("/analytics/trending", {"days":7}, [])
    if trending:
        df = pd.DataFrame(trending).set_index("name")
        st.bar_chart(df["count"], height=340)
    else: st.info("No trend data yet. Seed demo data or configure RSS feeds.")
with right:
    st.subheader("📰 Latest reports")
    for item in get("/incidents/latest", {"limit":6}, []): incident_card(item)
