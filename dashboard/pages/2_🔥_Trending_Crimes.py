import pandas as pd
import streamlit as st
from components.api import get
from components.ui import header, inject_css
st.set_page_config(page_title="Trending Crimes",page_icon="🔥",layout="wide"); inject_css(); header("🔥 Trending Crime Reports","Categories most frequently represented in collected news during the selected period")
days=st.slider("Window (days)",1,90,7)
data=get("/analytics/trending",{"days":days},[])
if data:
    df=pd.DataFrame(data); st.bar_chart(df.set_index("name")["count"],height=480); st.dataframe(df,use_container_width=True,hide_index=True)
else: st.info("No records yet.")
