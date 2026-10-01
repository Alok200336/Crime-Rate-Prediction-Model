import streamlit as st
from html import escape
from urllib.parse import urlsplit


def inject_css():
    st.markdown("""
    <style>
    .block-container {padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1350px;}
    .hero {padding: 1.7rem 1.8rem; border-radius: 20px; background: linear-gradient(135deg,#111827,#1f2937); color:white; margin-bottom:1.2rem;}
    .hero h1 {margin:0;font-size:2rem}.hero p{opacity:.8;margin:.4rem 0 0}
    .crime-card {border:1px solid rgba(128,128,128,.22); border-radius:16px; padding:1rem 1.1rem; margin:.65rem 0;}
    .badge {display:inline-block; padding:.2rem .55rem; border-radius:999px; border:1px solid rgba(128,128,128,.3); font-size:.75rem; margin-right:.35rem;}
    .muted {opacity:.65;font-size:.85rem}
    </style>""", unsafe_allow_html=True)


def header(title: str, subtitle: str):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def incident_card(item):
    item = {k: escape(v, quote=True) if isinstance(v, str) else v for k, v in item.items()}
    location = ", ".join(x for x in [item.get("city"), item.get("state")] if x) or "Location not extracted"
    source = item.get("source_name") or "Unknown source"
    url = item.get("article_url")
    if url and urlsplit(url).scheme not in {"http", "https"}: url = None
    link = f'<a href="{url}" target="_blank">Open source</a>' if url else ""
    st.markdown(f'''<div class="crime-card">
      <span class="badge">{item.get("crime_type","Crime")}</span><span class="badge">Severity {item.get("severity_score",1)}/5</span>
      <h4 style="margin:.6rem 0 .35rem">{item.get("title","")}</h4>
      <div class="muted">📍 {location} &nbsp; • &nbsp; {source} &nbsp; • &nbsp; Confidence {item.get("confidence_score",0):.0%}</div>
      <p>{item.get("summary") or "No summary available."}</p>{link}
    </div>''', unsafe_allow_html=True)
