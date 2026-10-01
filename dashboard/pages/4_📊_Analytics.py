import pandas as pd
import streamlit as st
from components.api import get
from components.ui import header, inject_css
st.set_page_config(page_title="Analytics",page_icon="📊",layout="wide"); inject_css(); header("📊 Crime News Analytics","Explore category, state and time trends in the collected news dataset")
days=st.select_slider("Analysis window", options=[7,14,30,60,90,180,365], value=30)
a,b=st.columns(2)
with a:
    st.subheader("By crime category"); d=get("/analytics/crime-types",{"days":days},[])
    if d: st.bar_chart(pd.DataFrame(d).set_index("name")["count"],height=370)
with b:
    st.subheader("By state"); d=get("/analytics/states",{"days":days},[])
    if d: st.bar_chart(pd.DataFrame(d).set_index("name")["count"],height=370)
st.subheader("Reports over time"); t=get("/analytics/trend",{"days":days},[])
if t:
    df=pd.DataFrame(t); df["date"]=pd.to_datetime(df["date"]); st.line_chart(df.set_index("date")["count"],height=330)
