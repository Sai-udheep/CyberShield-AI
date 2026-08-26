import streamlit as st
import pandas as pd
import os, sys
import tldextract
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.utils.shap_helper import url_predictor
from app.utils.database import log_scan
from app.utils.pdf_generator import generate_pdf_report
from app.utils.styles import inject_global_css

st.set_page_config(page_title="URL Scanner — CyberShield AI", layout="wide", initial_sidebar_state="collapsed")
inject_global_css()

st.markdown("## URL Scanner")
st.markdown("<p style='margin-top:-8px; color:#64748B;'>Analyze a web link for phishing indicators using XGBoost + SHAP explainability.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

tab_single, tab_batch = st.tabs(["Single scan", "Batch scan"])

# ═══════════════════════════ SINGLE SCAN ══════════════════════════════════════
with tab_single:
    st.markdown("<div class='cs-section-label'>Enter URL</div>", unsafe_allow_html=True)

    input_col, opt_col = st.columns([4, 1])
    with input_col:
        url_input = st.text_input("URL", placeholder="https://example.com", label_visibility="collapsed")
    with opt_col:
        fetch_html = st.checkbox("Deep scan", value=False,
                                  help="Fetch page HTML for extra features. Slightly slower.")

    run = st.button("Analyze", key="single_url_btn", use_container_width=False)

    if run:
        if not url_input.strip():
            st.warning("Enter a URL first.")
        else:
            # --- Homograph / IDN Attack Pre-check ---
            has_non_ascii = any(ord(c) > 127 for c in url_input)
            if has_non_ascii:
                st.warning(
                    "**Unicode Homograph Detected:** This URL contains non-ASCII characters "
                    "(e.g. Cyrillic or Greek letters that visually mimic Latin letters). "
                    "This is a classic IDN spoofing technique."
                )

            # --- IP Address Pre-check ---
            ext = tldextract.extract(url_input)
            domain = ext.domain + '.' + ext.suffix if ext.suffix else ext.domain

            with st.spinner("Running models..."):
                all_res = url_predictor.predict_all_and_ensemble(url_input, fetch_page=fetch_html)

            if "error" in all_res:
                st.error(all_res["error"])
            else:
                res_ablated = all_res["ablated"]
                res_full = all_res["full"]
                res_tfidf = all_res["tfidf"]
                res_ensemble = all_res["ensemble"]
                log_scan("URL", url_input, res_ensemble["prediction"], res_ensemble["probability"], res_ensemble["risk_score"])
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # 4-Model Tabs
                (sub_tab_ablated, sub_tab_ensemble, sub_tab_full, sub_tab_tfidf) = st.tabs([
                    "Primary Model (XGBoost Ablated)",
                    "Weighted Ensemble Model",
                    "Biased Model (XGBoost Full)",
                    "Alternative Model (TF-IDF Text)"
                ])
                
                BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                
                # --- 1. ABLATED MODEL RENDERING ---
                with sub_tab_ablated:
                    is_phish = res_ablated["prediction"] == "Phishing"
                    prob_pct = res_ablated["probability"] * 100
                    risk     = res_ablated["risk_score"]

                    fig_ab = None
                    if res_ablated["top_features"]:
                        fig_ab = url_predictor.generate_shap_plot(res_ablated["top_features"], res_ablated["prediction"])

                    verdict_col, shap_col = st.columns([1, 1], gap="large")
                    with verdict_col:
                        if is_phish:
                            st.markdown("""
                            <div class="cs-verdict-threat">
                              <div class="cs-verdict-title">Phishing threat detected</div>
                              <div class="cs-verdict-body">This URL exhibits characteristics associated with malicious phishing campaigns.</div>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="cs-verdict-safe">
                              <div class="cs-verdict-title">Verified secure</div>
                              <div class="cs-verdict-body">No suspicious indicators found. Link matches normal webpage characteristics.</div>
                            </div>""", unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)
                        m1, m2 = st.columns(2)
                        m1.markdown(f"""
                        <div class="cs-card" style="text-align:center;">
                          <div class="cs-metric-value" style="color:{'#EF4444' if risk > 50 else '#10B981'};">{risk}</div>
                          <div class="cs-metric-label">Risk Score / 100</div>
                        </div>""", unsafe_allow_html=True)
                        m2.markdown(f"""
                        <div class="cs-card" style="text-align:center;">
                          <div class="cs-metric-value">{prob_pct:.1f}%</div>
                          <div class="cs-metric-label">Model Confidence</div>
                        </div>""", unsafe_allow_html=True)

                    with shap_col:
                        st.markdown("<div class='cs-section-label'>SHAP feature attributions</div>", unsafe_allow_html=True)
                        if fig_ab:
                            st.pyplot(fig_ab, use_container_width=True)
                            plt.close(fig_ab)
                            st.markdown("<p style='font-size:0.78rem; color:#475569; text-align:center;'>Red bars push risk up · Blue bars push risk down</p>",
                                        unsafe_allow_html=True)
                        else:
                            st.info("SHAP values could not be computed for this prediction.")

                # --- 2. ENSEMBLE MODEL RENDERING ---
                with sub_tab_ensemble:
                    is_phish_ens = res_ensemble["prediction"] == "Phishing"
                    prob_pct_ens = res_ensemble["probability"] * 100
                    risk_ens     = res_ensemble["risk_score"]

                    fig_ens = None
                    if res_ensemble["top_features"]:
                        fig_ens = url_predictor.generate_shap_plot(res_ensemble["top_features"], res_ensemble["prediction"])

                    verdict_col_ens, shap_col_ens = st.columns([1, 1], gap="large")
                    with verdict_col_ens:
                        # Soft Voting Explanation Card
                        st.markdown("""
                        <div style="background-color: #0E1424; border: 1px solid #1D263B; padding: 12px 16px; border-radius: 6px; margin-bottom: 1.5rem;">
                          <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; font-family:'Syne',sans-serif; color:#00F0FF; font-weight:600; margin-bottom:4px;">Weighted Soft Voting (Probability Consensus)</div>
                          <div style="font-size:0.82rem; color:#94A3B8; line-height:1.4;">
                            Consensus Risk = (0.5 * Ablated XGBoost) + (0.3 * TF-IDF) + (0.2 * Full XGBoost). Combines structural, textual, and whitelist probabilities.
                          </div>
                        </div>""", unsafe_allow_html=True)

                        if is_phish_ens:
                            st.markdown("""
                            <div class="cs-verdict-threat">
                              <div class="cs-verdict-title">Phishing threat detected</div>
                              <div class="cs-verdict-body">The ensemble consensus indicates suspicious characteristics matching threat signatures.</div>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="cs-verdict-safe">
                              <div class="cs-verdict-title">Verified secure</div>
                              <div class="cs-verdict-body">Consensus vote checks out as legitimate. The link is secure to visit.</div>
                            </div>""", unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)
                        m1_ens, m2_ens = st.columns(2)
                        m1_ens.markdown(f"""
                        <div class="cs-card" style="text-align:center;">
                          <div class="cs-metric-value" style="color:{'#EF4444' if risk_ens > 50 else '#10B981'};">{risk_ens}</div>
                          <div class="cs-metric-label">Risk Score / 100</div>
                        </div>""", unsafe_allow_html=True)
                        m2_ens.markdown(f"""
                        <div class="cs-card" style="text-align:center;">
                          <div class="cs-metric-value">{prob_pct_ens:.1f}%</div>
                          <div class="cs-metric-label">Model Consensus Confidence</div>
                        </div>""", unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)
                        pdf_bytes = generate_pdf_report(
                            scan_type="URL", input_data=url_input,
                            prediction=res_ensemble["prediction"], confidence=res_ensemble["probability"],
                            risk_score=risk_ens, top_features=res_ensemble["top_features"],
                            shap_image_path=None, all_results=all_res
                        )
                        st.download_button("Download Consensus Report (PDF)", data=bytes(pdf_bytes),
                                           file_name="cybershield_consensus_report.pdf",
                                           mime="application/pdf", use_container_width=True)

                    with shap_col_ens:
                        st.markdown("<div class='cs-section-label'>Consolidated SHAP attributions</div>", unsafe_allow_html=True)
                        if fig_ens:
                            st.pyplot(fig_ens, use_container_width=True)
                            plt.close(fig_ens)
                            st.markdown("<p style='font-size:0.78rem; color:#475569; text-align:center;'>Weighted average of numerical features attributions</p>",
                                        unsafe_allow_html=True)
                        else:
                            st.info("SHAP values could not be computed for the ensemble.")

                # --- 3. BIASED MODEL RENDERING ---
                with sub_tab_full:
                    is_phish_fu = res_full["prediction"] == "Phishing"
                    prob_pct_fu = res_full["probability"] * 100
                    risk_fu     = res_full["risk_score"]

                    fig_fu = None
                    if res_full["top_features"]:
                        fig_fu = url_predictor.generate_shap_plot(res_full["top_features"], res_full["prediction"])

                    verdict_col_fu, shap_col_fu = st.columns([1, 1], gap="large")
                    with verdict_col_fu:
                        st.warning("**Ablation Warning:** This model is over-dependent on the `URLSimilarityIndex` feature (Alexa brand matching). If a URL is not on the whitelist, it is heavily biased towards Phishing.")

                        if is_phish_fu:
                            st.markdown("""
                            <div class="cs-verdict-threat">
                              <div class="cs-verdict-title">Phishing threat detected</div>
                              <div class="cs-verdict-body">Predicts phishing threat (potentially due to URLSimilarityIndex whitelist mismatch).</div>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="cs-verdict-safe">
                              <div class="cs-verdict-title">Verified secure</div>
                              <div class="cs-verdict-body">Identified as safe (strongly influenced by brand similarity score).</div>
                            </div>""", unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)
                        m1_fu, m2_fu = st.columns(2)
                        m1_fu.markdown(f"""
                        <div class="cs-card" style="text-align:center;">
                          <div class="cs-metric-value" style="color:{'#EF4444' if risk_fu > 50 else '#10B981'};">{risk_fu}</div>
                          <div class="cs-metric-label">Risk Score / 100</div>
                        </div>""", unsafe_allow_html=True)
                        m2_fu.markdown(f"""
                        <div class="cs-card" style="text-align:center;">
                          <div class="cs-metric-value">{prob_pct_fu:.1f}%</div>
                          <div class="cs-metric-label">Model Confidence</div>
                        </div>""", unsafe_allow_html=True)

                    with shap_col_fu:
                        st.markdown("<div class='cs-section-label'>Biased SHAP attributions</div>", unsafe_allow_html=True)
                        if fig_fu:
                            st.pyplot(fig_fu, use_container_width=True)
                            plt.close(fig_fu)
                            st.markdown("<p style='font-size:0.78rem; color:#475569; text-align:center;'>Red bars push risk up · Blue bars push risk down</p>",
                                        unsafe_allow_html=True)
                        else:
                            st.info("SHAP values could not be computed for this prediction.")

                # --- 4. TF-IDF MODEL RENDERING ---
                with sub_tab_tfidf:
                    if "error" in res_tfidf:
                        st.error(res_tfidf["error"])
                    else:
                        is_phish_tf = res_tfidf["prediction"] == "Phishing"
                        prob_pct_tf = res_tfidf["probability"] * 100
                        risk_tf     = res_tfidf["risk_score"]

                        fig_tf = None
                        if res_tfidf["top_features"]:
                            fig_tf = url_predictor.generate_shap_plot(res_tfidf["top_features"], res_tfidf["prediction"])

                        verdict_col_tf, shap_col_tf = st.columns([1, 1], gap="large")
                        with verdict_col_tf:
                            if is_phish_tf:
                                st.markdown("""
                                <div class="cs-verdict-threat">
                                  <div class="cs-verdict-title">Phishing threat detected</div>
                                  <div class="cs-verdict-body">This URL contains text sequences associated with malicious domains.</div>
                                </div>""", unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div class="cs-verdict-safe">
                                  <div class="cs-verdict-title">Verified secure</div>
                                  <div class="cs-verdict-body">Text sequences match normal domain profiles.</div>
                                </div>""", unsafe_allow_html=True)

                            st.markdown("<br>", unsafe_allow_html=True)
                            m1_tf, m2_tf = st.columns(2)
                            m1_tf.markdown(f"""
                            <div class="cs-card" style="text-align:center;">
                              <div class="cs-metric-value" style="color:{'#EF4444' if risk_tf > 50 else '#10B981'};">{risk_tf}</div>
                              <div class="cs-metric-label">Risk Score / 100</div>
                            </div>""", unsafe_allow_html=True)
                            m2_tf.markdown(f"""
                            <div class="cs-card" style="text-align:center;">
                              <div class="cs-metric-value">{prob_pct_tf:.1f}%</div>
                              <div class="cs-metric-label">Model Confidence</div>
                            </div>""", unsafe_allow_html=True)

                        with shap_col_tf:
                            st.markdown("<div class='cs-section-label'>Text N-Gram attributions</div>", unsafe_allow_html=True)
                            if fig_tf:
                                st.pyplot(fig_tf, use_container_width=True)
                                plt.close(fig_tf)
                                st.markdown("<p style='font-size:0.78rem; color:#475569; text-align:center;'>Red bars push risk up · Blue bars push risk down</p>",
                                            unsafe_allow_html=True)
                            else:
                                st.info("Text coefficients could not be computed for this prediction.")

# ═══════════════════════════ BATCH SCAN ═══════════════════════════════════════
with tab_batch:
    st.markdown("<div class='cs-section-label'>Paste URLs (one per line) or upload a file</div>", unsafe_allow_html=True)

    batch_input   = st.text_area("URLs", placeholder="https://site1.com\nhttps://site2.net",
                                  height=140, label_visibility="collapsed")
    uploaded_file = st.file_uploader("Or upload .txt / .csv", type=["txt", "csv"])

    links_to_scan = []
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            try:
                df_csv = pd.read_csv(uploaded_file)
                url_col = [c for c in df_csv.columns if "url" in c.lower() or "link" in c.lower()]
                links_to_scan = df_csv[url_col[0] if url_col else df_csv.columns[0]].dropna().tolist()
            except Exception as e:
                st.error(f"Could not parse CSV: {e}")
        else:
            links_to_scan = [ln.decode("utf-8").strip() for ln in uploaded_file if ln.strip()]
    elif batch_input.strip():
        links_to_scan = [ln.strip() for ln in batch_input.split("\n") if ln.strip()]

    if st.button("Run batch", key="batch_url_btn"):
        if not links_to_scan:
            st.warning("Add at least one URL.")
        else:
            results = []
            bar = st.progress(0)
            for i, link in enumerate(links_to_scan):
                all_res = url_predictor.predict_all_and_ensemble(link, fetch_page=False)
                if "error" not in all_res:
                    r_ab = all_res["ablated"]
                    r_fu = all_res["full"]
                    r_tf = all_res["tfidf"]
                    r_ens = all_res["ensemble"]
                    results.append({
                        "URL": link,
                        "Verdict (Consensus)": r_ens["prediction"],
                        "Risk (Consensus)": r_ens["risk_score"],
                        "Verdict (Ablated)": r_ab["prediction"],
                        "Risk (Ablated)": r_ab["risk_score"],
                        "Verdict (Full Biased)": r_fu["prediction"],
                        "Risk (Full Biased)": r_fu["risk_score"],
                        "Verdict (TF-IDF)": r_tf["prediction"],
                        "Risk (TF-IDF)": r_tf["risk_score"]
                    })
                    log_scan("URL (Batch)", link, r_ens["prediction"], r_ens["probability"], r_ens["risk_score"])
                bar.progress((i + 1) / len(links_to_scan))

            if results:
                df_r = pd.DataFrame(results)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div class='cs-section-label'>Results</div>", unsafe_allow_html=True)
                st.dataframe(df_r, use_container_width=True, hide_index=True)
                st.download_button("Export CSV", data=df_r.to_csv(index=False).encode(),
                                   file_name="url_batch_results.csv", mime="text/csv")
            else:
                st.error("No valid predictions were returned.")
