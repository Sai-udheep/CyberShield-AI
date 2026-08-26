import streamlit as st
import pandas as pd
import numpy as np
import os, sys, joblib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.utils.email_preprocessor import EmailPreprocessor, clean_text
from app.utils.database import log_scan
from app.utils.pdf_generator import generate_pdf_report
from app.utils.styles import inject_global_css

st.set_page_config(page_title="Email Scanner — CyberShield AI", layout="wide", initial_sidebar_state="collapsed")
inject_global_css()

BASE_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS_DIR = os.path.join(BASE_DIR, "models")

@st.cache_resource(show_spinner="Loading email model...")
def load_email_pipeline():
    pre   = EmailPreprocessor(vectorizer_path=os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib"))
    model = joblib.load(os.path.join(MODELS_DIR, "email_best_model.joblib"))
    return pre, model

preprocessor, model = load_email_pipeline()

st.markdown("## Email Scanner")
st.markdown("<p style='margin-top:-8px; color:#64748B;'>Paste an email to classify it as spam/phishing or legitimate. Trigger keywords are highlighted per prediction.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

tab_single, tab_batch = st.tabs(["Single scan", "Batch scan"])

# ═══════════════════════════ SINGLE SCAN ══════════════════════════════════════
with tab_single:
    sub_col, _ = st.columns([3, 1])
    with sub_col:
        st.markdown("<div class='cs-section-label'>Subject line (optional)</div>", unsafe_allow_html=True)
        email_subject = st.text_input("Subject", placeholder="Claim your prize now!", label_visibility="collapsed")

    st.markdown("<div class='cs-section-label' style='margin-top:10px;'>Message body</div>", unsafe_allow_html=True)
    email_body = st.text_area("Body", placeholder="Paste the raw email text here...",
                               height=180, label_visibility="collapsed")

    if st.button("Analyze", key="single_email_btn"):
        if not email_body.strip():
            st.warning("Paste an email body first.")
        elif model is None:
            st.error("Email model failed to load.")
        else:
            full_text = f"{email_subject}\n{email_body}"
            with st.spinner("Classifying..."):
                X_vec    = preprocessor.transform([full_text])
                prob_spam = float(model.predict_proba(X_vec)[0][1])
                pred     = "Spam" if prob_spam >= 0.5 else "Ham"
                risk     = int(prob_spam * 100)
                prob_winning = prob_spam if pred == "Spam" else (1.0 - prob_spam)
                prob_pct = prob_winning * 100

            log_scan("Email",
                     f"Subject: {email_subject} | {email_body[:80]}...",
                     pred, prob_winning, risk)

            st.markdown("<br>", unsafe_allow_html=True)
            res_col, kw_col = st.columns([1, 1], gap="large")

            with res_col:
                is_spam = pred == "Spam"
                if is_spam:
                    st.markdown("""
                    <div class="cs-verdict-threat">
                      <div class="cs-verdict-title">Spam / phishing detected</div>
                      <div class="cs-verdict-body">Text patterns match unsolicited spam or phishing campaigns.</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="cs-verdict-safe">
                      <div class="cs-verdict-title">Legitimate email</div>
                      <div class="cs-verdict-body">Text matches characteristic patterns of regular communication.</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.markdown(f"""
                <div class="cs-card" style="text-align:center;">
                  <div class="cs-metric-value" style="color:{'#EF4444' if risk > 50 else '#10B981'};">{risk}</div>
                  <div class="cs-metric-label">Spam Score / 100</div>
                </div>""", unsafe_allow_html=True)
                m2.markdown(f"""
                <div class="cs-card" style="text-align:center;">
                  <div class="cs-metric-value">{prob_pct:.1f}%</div>
                  <div class="cs-metric-label">Confidence</div>
                </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # ── Trigger keyword attribution ──────────────────────────────
                word_attributions = []
                cleaned_words = clean_text(full_text).split()

                # Support both: direct LinearSVC coef_ OR wrapped CalibratedClassifierCV
                def get_coefs(m):
                    if hasattr(m, "coef_"):
                        c = m.coef_
                        return c.toarray()[0] if hasattr(c, "toarray") else np.array(c).flatten()
                    if hasattr(m, "calibrated_classifiers_"):
                        inner = m.calibrated_classifiers_[0].estimator
                        if hasattr(inner, "coef_"):
                            c = inner.coef_
                            return c.toarray()[0] if hasattr(c, "toarray") else np.array(c).flatten()
                    return None

                coefs = get_coefs(model)
                if coefs is not None:
                    vocab = preprocessor.vectorizer.vocabulary_   # dict: word -> index (O(1))
                    seen  = set()
                    for w in cleaned_words:
                        if w in vocab and w not in seen:
                            seen.add(w)
                            wt = float(coefs[vocab[w]])
                            if wt > 0:
                                word_attributions.append((w, wt))
                    word_attributions.sort(key=lambda x: x[1], reverse=True)

                pdf_features = [(w, wt, "Present") for w, wt in word_attributions] or [("N/A", 0.0, "N/A")]
                pdf_bytes = generate_pdf_report(
                    scan_type="Email", input_data=full_text,
                    prediction=pred, confidence=prob_winning,
                    risk_score=risk, top_features=pdf_features
                )
                st.download_button("Download PDF report", data=bytes(pdf_bytes),
                                   file_name="cybershield_email_report.pdf",
                                   mime="application/pdf", use_container_width=True)

            with kw_col:
                st.markdown("<div class='cs-section-label'>Trigger keywords</div>", unsafe_allow_html=True)
                if word_attributions:
                    badges = "".join(
                        f'<span class="cs-badge">{w} +{wt:.2f}</span>'
                        for w, wt in word_attributions[:10]
                    )
                    st.markdown(f"<div style='line-height:2;'>{badges}</div>", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:0.78rem; color:#475569; margin-top:10px;'>Words that pushed the model toward Spam, ranked by SVM coefficient weight.</p>",
                                unsafe_allow_html=True)
                else:
                    st.info("No strong spam-correlated keywords identified.")

# ═══════════════════════════ BATCH SCAN ═══════════════════════════════════════
with tab_batch:
    st.markdown("<div class='cs-section-label'>Upload a CSV with email text</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("CSV file", type=["csv"], label_visibility="collapsed")

    if uploaded:
        try:
            df_csv = pd.read_csv(uploaded)
            st.dataframe(df_csv.head(3), use_container_width=True, hide_index=True)
            selected_col = st.selectbox("Column containing email text:", df_csv.columns)

            if st.button("Run batch", key="batch_email_btn"):
                results = []
                bar     = st.progress(0)
                texts   = df_csv[selected_col].dropna().tolist()
                for i, text in enumerate(texts):
                    X    = preprocessor.transform([str(text)])
                    prob_spam = float(model.predict_proba(X)[0][1])
                    pred = "Spam" if prob_spam >= 0.5 else "Ham"
                    rs   = int(prob_spam * 100)
                    prob_winning = prob_spam if pred == "Spam" else (1.0 - prob_spam)
                    results.append({"Snippet": str(text)[:80] + "…", "Verdict": pred,
                                    "Score": rs, "Confidence": f"{prob_winning*100:.1f}%"})
                    log_scan("Email", str(text)[:150], pred, prob_winning, rs)
                    bar.progress((i + 1) / len(texts))

                df_r = pd.DataFrame(results)
                st.markdown("<div class='cs-section-label' style='margin-top:14px;'>Results</div>", unsafe_allow_html=True)
                st.dataframe(df_r, use_container_width=True, hide_index=True)
                st.download_button("Export CSV", data=df_r.to_csv(index=False).encode(),
                                   file_name="email_batch_results.csv", mime="text/csv")
        except Exception as e:
            st.error(f"Could not parse CSV: {e}")
