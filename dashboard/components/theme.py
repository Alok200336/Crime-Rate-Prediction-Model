import streamlit as st

def apply_theme():
    st.markdown('''
    <style>
    .block-container{padding-top:1.5rem;padding-bottom:3rem;max-width:1450px}
    [data-testid="stMetric"]{background:#111827;border:1px solid #283445;border-radius:16px;padding:14px}
    .hero{padding:26px 28px;border-radius:20px;background:linear-gradient(135deg,#111827,#1f2937);border:1px solid #334155;margin-bottom:20px}
    .hero h1{margin:0;font-size:2.05rem}.hero p{color:#cbd5e1;margin:.45rem 0 0}
    .badge{display:inline-block;font-size:.75rem;background:#1d4ed8;color:white;border-radius:999px;padding:5px 10px;margin-bottom:10px}
    .incident{border:1px solid #334155;border-radius:16px;padding:16px;margin:10px 0;background:#0f172a}
    .incident small{color:#94a3b8}.incident h4{margin:.35rem 0}.muted{color:#94a3b8}
    .empty{padding:24px;border:1px dashed #475569;border-radius:14px;color:#94a3b8;text-align:center}
    </style>''',unsafe_allow_html=True)

def hero(title, subtitle, badge='Crime Intelligence India'):
    st.markdown(f'<div class="hero"><span class="badge">{badge}</span><h1>{title}</h1><p>{subtitle}</p></div>',unsafe_allow_html=True)
