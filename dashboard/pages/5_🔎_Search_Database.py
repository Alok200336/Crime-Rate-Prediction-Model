import pandas as pd
import streamlit as st
from components.api import get
from components.ui import header, inject_css
st.set_page_config(page_title="Search",page_icon="🔎",layout="wide"); inject_css(); header("🔎 Search Crime Database","Search normalized reports and export the filtered dataset")
meta=get("/meta/filters",default={"crime_types":[],"states":[]}); a,b,c=st.columns([2,1,1]); q=a.text_input("Keyword"); ct=b.selectbox("Crime type",[""]+meta.get("crime_types",[])); state=c.selectbox("State",[""]+meta.get("states",[]))
rows=get("/incidents/search",{"q":q or None,"crime_type":ct or None,"state":state or None,"limit":500},[])
if rows:
    df=pd.DataFrame(rows); st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("Download filtered CSV",df.to_csv(index=False).encode(),"crime_news_dataset.csv","text/csv")
else: st.info("No matching records.")
