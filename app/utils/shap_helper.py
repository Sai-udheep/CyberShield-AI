import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
import streamlit as st
from app.utils.url_extractor import get_url_features_df, NUMERIC_FEATURES, to_punycode_url

# Determine base directory dynamically for absolute paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Full Model Paths (Model A)
SCALER_FULL_PATH = os.path.join(MODELS_DIR, "url_scaler_full.joblib")
MODEL_FULL_PATH = os.path.join(MODELS_DIR, "url_model_full.joblib")
EXPLAINER_FULL_PATH = os.path.join(MODELS_DIR, "url_shap_explainer_full.joblib")
FEATURES_FULL_PATH = os.path.join(MODELS_DIR, "url_feature_names_full.joblib")

# Ablated Model Paths (Model B)
SCALER_ABLATED_PATH = os.path.join(MODELS_DIR, "url_scaler_ablated.joblib")
MODEL_ABLATED_PATH = os.path.join(MODELS_DIR, "url_model_ablated.joblib")
EXPLAINER_ABLATED_PATH = os.path.join(MODELS_DIR, "url_shap_explainer_ablated.joblib")
FEATURES_ABLATED_PATH = os.path.join(MODELS_DIR, "url_feature_names_ablated.joblib")

# TF-IDF Paths (Model C)
TFIDF_VECTORIZER_PATH = os.path.join(MODELS_DIR, "url_tfidf_vectorizer.joblib")
TFIDF_MODEL_PATH = os.path.join(MODELS_DIR, "url_tfidf_model.joblib")

class URLPredictor:
    def __init__(self):
        # Model A (Full)
        self.scaler_full = None
        self.model_full = None
        self.explainer_full = None
        self.features_full = None
        
        # Model B (Ablated)
        self.scaler_ablated = None
        self.model_ablated = None
        self.explainer_ablated = None
        self.features_ablated = None
        
        # Model C (TF-IDF)
        self.tfidf_vectorizer = None
        self.tfidf_model = None
        
        self.load_artifacts()

    def load_artifacts(self):
        """Loads serialized machine learning, SHAP, and TF-IDF artifacts for all versions."""
        try:
            # Load Model A (Full)
            if os.path.exists(SCALER_FULL_PATH):
                self.scaler_full = joblib.load(SCALER_FULL_PATH)
            if os.path.exists(MODEL_FULL_PATH):
                self.model_full = joblib.load(MODEL_FULL_PATH)
            if os.path.exists(EXPLAINER_FULL_PATH):
                self.explainer_full = joblib.load(EXPLAINER_FULL_PATH)
            if os.path.exists(FEATURES_FULL_PATH):
                self.features_full = joblib.load(FEATURES_FULL_PATH)
                
            # Load Model B (Ablated)
            if os.path.exists(SCALER_ABLATED_PATH):
                self.scaler_ablated = joblib.load(SCALER_ABLATED_PATH)
            if os.path.exists(MODEL_ABLATED_PATH):
                self.model_ablated = joblib.load(MODEL_ABLATED_PATH)
            if os.path.exists(EXPLAINER_ABLATED_PATH):
                self.explainer_ablated = joblib.load(EXPLAINER_ABLATED_PATH)
            if os.path.exists(FEATURES_ABLATED_PATH):
                self.features_ablated = joblib.load(FEATURES_ABLATED_PATH)
                
            # Load Model C (TF-IDF)
            if os.path.exists(TFIDF_VECTORIZER_PATH):
                self.tfidf_vectorizer = joblib.load(TFIDF_VECTORIZER_PATH)
            if os.path.exists(TFIDF_MODEL_PATH):
                self.tfidf_model = joblib.load(TFIDF_MODEL_PATH)
        except Exception as e:
            print(f"Error loading URL model artifacts: {e}")

    def predict_xgb_from_df(self, raw_features_df, model_type="ablated"):
        """
        Executes a prediction using the specified XGBoost model (Full or Ablated) 
        from a pre-extracted raw features DataFrame to avoid redundant extraction.
        """
        # Select appropriate model components
        if model_type == "full":
            scaler = self.scaler_full
            model = self.model_full
            explainer = self.explainer_full
            # Full features list includes URLSimilarityIndex
            feature_cols = self.features_full if self.features_full else NUMERIC_FEATURES
        else:
            scaler = self.scaler_ablated
            model = self.model_ablated
            explainer = self.explainer_ablated
            # Ablated features list drops URLSimilarityIndex
            if self.features_ablated:
                feature_cols = self.features_ablated
            else:
                feature_cols = [f for f in NUMERIC_FEATURES if f != "URLSimilarityIndex"]

        if model is None or scaler is None:
            return {"error": f"URL Classifier ({model_type}) is not initialized."}

        # Select only the features the specific model expects in the correct training order
        df_for_model = raw_features_df[feature_cols].copy()
        
        # 1. Scale features
        scaled_features = scaler.transform(df_for_model)
        
        # 2. Neutralize HTML features if missing (prevent scale shift bias)
        html_start_idx = feature_cols.index("LineOfCode")
        html_features_missing = (df_for_model.iloc[0]["LineOfCode"] == 0.0 and 
                                 df_for_model.iloc[0]["NoOfImage"] == 0.0)
        if html_features_missing:
            scaled_features[0, html_start_idx:] = 0.0

        # 3. Predict probability (Class 0 = Phishing, Class 1 = Safe)
        probs = model.predict_proba(scaled_features)[0]
        prob_phishing = float(probs[0])
        prob_safe = float(probs[1])
        
        prediction = "Phishing" if prob_phishing >= 0.5 else "Safe"
        probability = prob_phishing if prediction == "Phishing" else prob_safe
        risk_score = int(prob_phishing * 100)

        # 4. Generate SHAP explainability
        top_features = []
        shap_array = None
        if explainer is not None:
            try:
                sh_vals = explainer(scaled_features)
                if hasattr(sh_vals, "values"):
                    shap_array = sh_vals.values[0]
                else:
                    shap_array = sh_vals[0]
                if len(shap_array.shape) > 1 and shap_array.shape[1] == 2:
                    shap_array = shap_array[:, 1]
            except Exception:
                try:
                    sh_vals = explainer.shap_values(scaled_features)
                    if isinstance(sh_vals, list):
                        shap_array = sh_vals[1][0] if len(sh_vals) > 1 else sh_vals[0][0]
                    else:
                        shap_array = sh_vals[0] if len(sh_vals.shape) > 1 else sh_vals
                except Exception:
                    pass

            if shap_array is not None:
                # Multiply by -1 so positive values push towards Phishing (Class 0)
                feature_contribs = []
                for name, s_val in zip(feature_cols, shap_array):
                    actual_val = df_for_model.iloc[0][name]
                    feature_contribs.append((name, -float(s_val), float(actual_val)))
                top_features = sorted(feature_contribs, key=lambda x: abs(x[1]), reverse=True)

        return {
            "prediction": prediction,
            "probability": probability,
            "risk_score": risk_score,
            "top_features": top_features,
            "shap_raw": {name: -float(s) for name, s in zip(feature_cols, shap_array)} if shap_array is not None else None,
            "raw_features": df_for_model.to_dict(orient='records')[0]
        }

    def predict_and_explain(self, url, fetch_page=False, model_type="ablated"):
        """
        Primary entry point (maintaining backward compatibility). Extracts features and runs predictions.
        """
        # Run raw feature extraction exactly once
        raw_features_df = get_url_features_df(url, fetch_page=fetch_page)
        return self.predict_xgb_from_df(raw_features_df, model_type=model_type)

    def predict_tfidf(self, url):
        """
        Predicts whether a URL is phishing using TF-IDF and returns feature coefficients weights.
        """
        if self.tfidf_model is None or self.tfidf_vectorizer is None:
            return {"error": "TF-IDF URL Classifier is not initialized or trained."}
            
        url_puny = to_punycode_url(url)
        url_lower = url_puny.lower()
        vec_features = self.tfidf_vectorizer.transform([url_lower])
        
        # Predict probability (Class 0 = Phishing, Class 1 = Safe)
        probs = self.tfidf_model.predict_proba(vec_features)[0]
        prob_phishing = float(probs[0])
        prob_safe = float(probs[1])
        
        prediction = "Phishing" if prob_phishing >= 0.5 else "Safe"
        probability = prob_phishing if prediction == "Phishing" else prob_safe
        risk_score = int(prob_phishing * 100)
        
        top_features = []
        try:
            non_zero_indices = vec_features.nonzero()[1]
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            coefs = self.tfidf_model.coef_[0]
            
            feature_contribs = []
            for idx in non_zero_indices:
                ngram = feature_names[idx]
                tf_idf_val = vec_features[0, idx]
                weight = coefs[idx]
                # Multiply by -1 so positive values push towards Phishing (Class 0)
                impact = -float(tf_idf_val * weight)
                feature_contribs.append((f"'{ngram}'", impact, float(tf_idf_val)))
                
            top_features = sorted(feature_contribs, key=lambda x: abs(x[1]), reverse=True)
        except Exception as e:
            print(f"TF-IDF explainability error: {e}")
            
        return {
            "prediction": prediction,
            "probability": probability,
            "risk_score": risk_score,
            "top_features": top_features
        }

    def predict_all_and_ensemble(self, url, fetch_page=False):
        """
        High-performance short-circuit pipeline. Extracts raw features exactly once,
        runs all three sub-models, and aggregates predictions into a weighted Soft Voting ensemble.
        """
        # 1. Extract raw features exactly once
        raw_features_df = get_url_features_df(url, fetch_page=fetch_page)
        
        # 2. Run Model A (Full features)
        res_full = self.predict_xgb_from_df(raw_features_df, model_type="full")
        
        # 3. Run Model B (Ablated features)
        res_ablated = self.predict_xgb_from_df(raw_features_df, model_type="ablated")
        
        # 4. Run Model C (TF-IDF)
        res_tfidf = self.predict_tfidf(url)
        
        # Check errors
        if "error" in res_full:
            return {"error": res_full["error"]}
        if "error" in res_ablated:
            return {"error": res_ablated["error"]}
        if "error" in res_tfidf:
            return {"error": res_tfidf["error"]}

        # 5. Soft Voting (Probability Averaging)
        p_full = res_full["risk_score"] / 100.0
        p_ablated = res_ablated["risk_score"] / 100.0
        p_tfidf = res_tfidf["risk_score"] / 100.0
        
        p_ensemble = (0.2 * p_full) + (0.5 * p_ablated) + (0.3 * p_tfidf)
        
        prediction_ens = "Phishing" if p_ensemble >= 0.5 else "Safe"
        prob_ens = p_ensemble if prediction_ens == "Phishing" else (1.0 - p_ensemble)
        risk_ens = int(p_ensemble * 100)

        # 6. Ensemble SHAP Explainability (Weighted SHAP values for numerical features)
        ensemble_shap_contribs = []
        if res_full.get("shap_raw") and res_ablated.get("shap_raw"):
            shap_full = res_full["shap_raw"]
            shap_ablated = res_ablated["shap_raw"]
            
            # Combine the two explainers (Weights: Model A = 0.2/0.7, Model B = 0.5/0.7)
            w_full = 0.2 / 0.7
            w_ablated = 0.5 / 0.7
            
            feature_cols_ablated = self.features_ablated if self.features_ablated else [f for f in NUMERIC_FEATURES if f != "URLSimilarityIndex"]
            for name in feature_cols_ablated:
                s_full = shap_full.get(name, 0.0)
                s_ablated = shap_ablated.get(name, 0.0)
                
                s_ens = (w_full * s_full) + (w_ablated * s_ablated)
                actual_val = raw_features_df.iloc[0][name]
                ensemble_shap_contribs.append((name, s_ens, float(actual_val)))
                
            ensemble_shap_contribs = sorted(ensemble_shap_contribs, key=lambda x: abs(x[1]), reverse=True)

        return {
            "full": res_full,
            "ablated": res_ablated,
            "tfidf": res_tfidf,
            "ensemble": {
                "prediction": prediction_ens,
                "probability": prob_ens,
                "risk_score": risk_ens,
                "top_features": ensemble_shap_contribs
            }
        }

    def generate_shap_plot(self, top_features, prediction):
        """
        Creates a customized horizontal bar chart showing top SHAP feature contributions.
        """
        features_to_plot = top_features[:8]
        features_to_plot.reverse()
        
        names = [f[0] for f in features_to_plot]
        values = [f[1] for f in features_to_plot]
        
        colors = ['#F43F5E' if v > 0 else '#0EA5E9' for v in values]
        
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.barh(names, values, color=colors, height=0.6)
        
        fig.patch.set_facecolor('#0F172A')
        ax.set_facecolor('#1E293B')
        
        ax.tick_params(colors='white', labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#475569')
        ax.spines['bottom'].set_color('#475569')
        
        ax.axvline(0, color='white', linewidth=0.8, linestyle='--')
        
        ax.set_title("Feature Influence (SHAP Values)", color='white', fontsize=11, pad=10, weight='bold')
        ax.set_xlabel("Impact Score (+ Phishing / - Safe)", color='#94A3B8', fontsize=9)
        
        plt.tight_layout()
        return fig

@st.cache_resource(show_spinner="Loading URL threat model...")
def get_url_predictor():
    return URLPredictor()

url_predictor = get_url_predictor()
