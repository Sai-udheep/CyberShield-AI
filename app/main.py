import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.utils.database import init_db, get_stats
from app.utils.styles import inject_global_css

st.set_page_config(
    page_title="CyberShield AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)
init_db()
inject_global_css()

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 32px 0 20px 0; border-bottom: 1px solid #1D263B; margin-bottom: 28px;">
  <div style="display:flex; align-items:center; gap:14px; margin-bottom:8px;">
    <h1 style="margin:0;">CyberShield AI</h1>
  </div>
  <p style="margin:0; font-size:1rem; color:#64748B;">
    Phishing detection, email classification, and explainable threat analysis — all offline.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Stats row ──────────────────────────────────────────────────────────────────
stats = get_stats()
rate  = stats["threat_rate"]
rate_color = "#10B981" if rate < 20 else "#F59E0B" if rate < 50 else "#EF4444"

c1, c2, c3, c4 = st.columns(4)
for col, label, val, color in [
    (c1, "Total Scans",    stats["total_scans"],  "#F1F5F9"),
    (c2, "Threats Flagged", stats["threat_scans"], "#EF4444"),
    (c3, "Safe Scans",     stats["safe_scans"],   "#10B981"),
    (c4, "Threat Rate",    f"{rate}%",            rate_color),
]:
    col.markdown(f"""
    <div class="cs-card">
      <div class="cs-metric-value" style="color:{color};">{val}</div>
      <div class="cs-metric-label">{label}</div>
    </div>""", unsafe_allow_html=True)

# ── Navigation ─────────────────────────────────────────────────────────────────
st.markdown("<div class='cs-section-label' style='margin-top:8px;'>Go to</div>", unsafe_allow_html=True)

nav1, nav2 = st.columns(2)
with nav1:
    st.page_link("pages/1_URL_Scanner.py",      label="URL Scanner")
    st.page_link("pages/3_Model_Comparison.py", label="Model Comparison")
    st.page_link("pages/5_Scan_History.py",     label="Scan History")
with nav2:
    st.page_link("pages/2_Email_Scanner.py",    label="Email Scanner")
    st.page_link("pages/4_Cyber_Assistant.py",  label="Cyber Assistant")

# ── About strip ────────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:28px; border-top:1px solid #1E293B; padding-top:20px;'>", unsafe_allow_html=True)
a, b = st.columns(2)
with a:
    st.markdown("""
    <div class="cs-card">
      <div class="cs-section-label">URL detection</div>
      <p style="margin:4px 0 0 0; color:#CBD5E1; font-size:0.9rem;">
        XGBoost trained on 50 lexical and HTML features. SHAP values reveal exactly which
        indicators drove each verdict.
      </p>
    </div>""", unsafe_allow_html=True)
with b:
    st.markdown("""
    <div class="cs-card">
      <div class="cs-section-label">Email detection</div>
      <p style="margin:4px 0 0 0; color:#CBD5E1; font-size:0.9rem;">
        Linear SVM on TF-IDF vectors, tuned for 100% precision — zero legitimate emails
        misclassified. Trigger keywords highlighted per prediction.
      </p>
    </div>""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
