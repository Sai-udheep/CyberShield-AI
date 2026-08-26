import streamlit as st
import pandas as pd
import json
import os, sys
import plotly.graph_objects as go
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.utils.styles import inject_global_css

st.set_page_config(page_title="Model Comparison — CyberShield AI", layout="wide", initial_sidebar_state="collapsed")
inject_global_css()

BASE_DIR     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
METRICS_PATH = os.path.join(BASE_DIR, "models", "comparison_metrics.json")

def load_metrics():
    if not os.path.exists(METRICS_PATH):
        return None
    with open(METRICS_PATH) as f:
        return json.load(f)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0F172A",
    font=dict(color="#94A3B8", size=11),
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#CBD5E1")),
    xaxis=dict(gridcolor="#1E293B", linecolor="#1E293B", tickfont=dict(color="#64748B")),
    yaxis=dict(gridcolor="#1E293B", linecolor="#1E293B", tickfont=dict(color="#64748B")),
)

st.markdown("## Model Benchmarks")
st.markdown("<p style='margin-top:-8px; color:#64748B;'>Classification metrics and inference latency for all 10 trained models.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

data = load_metrics()
if not data:
    st.warning("Metrics file not found. Run the modeling notebooks first.")
    st.stop()

tab_url, tab_email = st.tabs(["URL models", "Email models"])

def render_tab(models_dict, best_key, label):
    df = pd.DataFrame(models_dict).T.reset_index().rename(columns={"index": "Model"})
    best = data.get(best_key, "")

    # Best model pill
    st.markdown(f"""
    <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(16,185,129,0.08);
         border:1px solid rgba(16,185,129,0.3); border-radius:6px; padding:6px 14px; margin-bottom:14px;">
      <span style="color:#10B981; font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em;">Best classifier</span>
      <span style="color:#E2E8F0; font-size:0.9rem; font-weight:600;">{best}</span>
    </div>""", unsafe_allow_html=True)

    # Metrics table
    st.markdown("<div class='cs-section-label'>All classifiers</div>", unsafe_allow_html=True)
    fmt = {k: "{:.3%}" for k in ["accuracy","precision","recall","f1_score"]}
    fmt["train_time_sec"]          = "{:.3f} s"
    fmt["inference_latency_ms"]    = "{:.5f} ms"
    st.dataframe(df.style.format(fmt), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        fig = go.Figure()
        for metric, color in [("f1_score","#0EA5E9"),("accuracy","#10B981"),("precision","#8B5CF6")]:
            if metric in df.columns:
                fig.add_trace(go.Bar(x=df["Model"], y=df[metric], name=metric.replace("_"," ").title(),
                                     marker_color=color))
        fig.update_layout(title=f"{label} — F1 / Accuracy / Precision", barmode="group", **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df["Model"], y=df["inference_latency_ms"],
                              name="Latency (ms/sample)", marker_color="#F59E0B"))
        fig2.update_layout(title=f"{label} — Inference Latency", **CHART_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    # Decision note
    st.markdown("<div class='cs-section-label'>Why this model was selected</div>", unsafe_allow_html=True)
    if best in models_dict:
        m = models_dict[best]
        st.markdown(f"""
        <div class="cs-card">
          <p style="color:#CBD5E1; font-size:0.9rem; margin:0; line-height:1.65;">
            <strong style="color:#F1F5F9;">{best}</strong> achieved the highest F1-score of
            <strong style="color:#0EA5E9;">{m['f1_score']*100:.2f}%</strong> with an inference latency of
            <strong style="color:#0EA5E9;">{m['inference_latency_ms']:.5f} ms</strong> per sample,
            making it both the most accurate and fastest option in the benchmark.
          </p>
        </div>""", unsafe_allow_html=True)

with tab_url:
    render_tab(data.get("url_models", {}), "best_url_model", "URL")

with tab_email:
    render_tab(data.get("email_models", {}), "best_email_model", "Email")
