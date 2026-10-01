import pandas as pd
import streamlit as st
from components.api import get
from components.ui import header, inject_css
st.set_page_config(page_title="Crime Map",page_icon="🗺️",layout="wide"); inject_css(); header("🗺️ Crime Map","Geographic view of reports where a city/location was extracted")
items=get("/incidents/search",{"limit":500},[])
rows=[x for x in items if x.get("latitude") is not None and x.get("longitude") is not None]
if rows:
    df=pd.DataFrame(rows).rename(columns={"latitude":"lat","longitude":"lon"})
    crime_types=sorted(df.crime_type.dropna().unique()); selected=st.multiselect("Crime types",crime_types,default=crime_types)
    df=df[df.crime_type.isin(selected)]
    st.map(df[["lat","lon"]],size=55)
    st.dataframe(df[["crime_type","title","city","state","source_name"]],use_container_width=True,hide_index=True)
else: st.info("No geocoded incidents available yet.")
