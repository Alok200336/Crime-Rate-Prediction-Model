import pandas as pd

def incidents_df(items):
    df = pd.DataFrame(items or [])
    if df.empty: return df
    for c in ['published_at','created_at','incident_date']:
        if c in df: df[c]=pd.to_datetime(df[c],errors='coerce')
    return df

def count_df(items):
    df=pd.DataFrame(items or [])
    if not df.empty: df=df.rename(columns={'name':'label'})
    return df

def trend_df(items):
    df=pd.DataFrame(items or [])
    if not df.empty: df['date']=pd.to_datetime(df['date'],errors='coerce')
    return df
