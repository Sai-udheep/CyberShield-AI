import streamlit as st
import pandas as pd
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.utils.database import get_history, clear_history
from app.utils.styles import inject_global_css

st.set_page_config(page_title="Scan History — CyberShield AI", layout="wide", initial_sidebar_state="collapsed")
inject_global_css()

st.markdown("## Scan History")
st.markdown("<p style='margin-top:-8px; color:#64748B;'>Browse, filter, and export every threat scan recorded on this device.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

df = get_history()

if df.empty:
    st.info("No scan records yet. Run a URL or email scan to start building the log.")
    st.stop()

# ── Filters row ────────────────────────────────────────────────────────────────
st.markdown("<div class='cs-section-label'>Filters</div>", unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns([1.5, 1.5, 2.5, 1])

with f1:
    type_opts = df["scan_type"].unique().tolist()
    type_sel  = st.multiselect("Scan type", type_opts, default=type_opts, label_visibility="visible")

with f2:
    pred_opts = df["prediction"].unique().tolist()
    pred_sel  = st.multiselect("Verdict", pred_opts, default=pred_opts, label_visibility="visible")

with f3:
    search = st.text_input("Search input data", placeholder="domain, keyword…", label_visibility="visible")

with f4:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    if st.button("Clear all logs", use_container_width=True):
        st.session_state["confirm_clear"] = True

# Confirm clear dialog
if st.session_state.get("confirm_clear"):
    st.warning("This will permanently delete all scan records. Confirm?")
    yes, no = st.columns([1, 3])
    if yes.button("Yes, delete", type="primary"):
        clear_history()
        st.session_state["confirm_clear"] = False
        st.success("All records cleared.")
        st.rerun()
    if no.button("Cancel"):
        st.session_state["confirm_clear"] = False
        st.rerun()

# Apply filters
filtered = df[df["scan_type"].isin(type_sel) & df["prediction"].isin(pred_sel)]
if search.strip():
    filtered = filtered[filtered["input_data"].str.contains(search.strip(), case=False, na=False)]

st.markdown("<br>", unsafe_allow_html=True)

# ── Summary strip ──────────────────────────────────────────────────────────────
n_total   = len(filtered)
n_threats = (filtered["prediction"].isin(["Phishing","Spam"])).sum()
n_safe    = n_total - n_threats

s1, s2, s3 = st.columns(3)
for col, val, label, color in [
    (s1, n_total,   "Records shown",    "#F1F5F9"),
    (s2, n_threats, "Threats",          "#EF4444"),
    (s3, n_safe,    "Safe",             "#10B981"),
]:
    col.markdown(f"""
    <div class="cs-card" style="text-align:center; padding:14px;">
      <div class="cs-metric-value" style="color:{color}; font-size:1.6rem;">{val}</div>
      <div class="cs-metric-label">{label}</div>
    </div>""", unsafe_allow_html=True)

# ── Table ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='cs-section-label' style='margin-top:4px;'>Records</div>", unsafe_allow_html=True)

display = filtered.copy()
try:
    display["timestamp"] = pd.to_datetime(display["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
except Exception:
    pass
display.columns = ["ID", "Date", "Type", "Input", "Verdict", "Confidence", "Risk Score"]

st.dataframe(display, use_container_width=True, hide_index=True)

# ── Export ─────────────────────────────────────────────────────────────────────
st.download_button(
    "Export to CSV",
    data=filtered.to_csv(index=False).encode(),
    file_name="cybershield_history.csv",
    mime="text/csv"
)
