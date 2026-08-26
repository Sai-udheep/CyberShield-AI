import os
import joblib
import pandas as pd
import numpy as np

# Set paths
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))
URL_MODEL_PATH = os.path.join(MODELS_DIR, "url_best_model.joblib")
URL_SCALER_PATH = os.path.join(MODELS_DIR, "url_scaler.joblib")
EMAIL_MODEL_PATH = os.path.join(MODELS_DIR, "email_best_model.joblib")
EMAIL_VEC_PATH = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")

def inspect_url_model():
    print("=" * 60)
    print("URL CLASSIFIER DIAGNOSTICS")
    print("=" * 60)
    
    if not os.path.exists(URL_MODEL_PATH) or not os.path.exists(URL_SCALER_PATH):
        print("URL model or scaler files are missing in models/ directory.")
        return
        
    model = joblib.load(URL_MODEL_PATH)
    scaler = joblib.load(URL_SCALER_PATH)
    
    print(f"Model Class:      {type(model).__name__}")
    print(f"Scaler Class:     {type(scaler).__name__}")
    print(f"Number of Inputs: {scaler.n_features_in_} features")
    
    # Print a few hyperparameter properties
    if hasattr(model, "get_params"):
        params = model.get_params()
        print("\nHyperparameters:")
        for k in ['objective', 'learning_rate', 'max_depth', 'n_estimators', 'random_state']:
            if k in params:
                print(f"  {k}: {params[k]}")
                
    # Print scaling statistics
    print("\nScaler Baseline Stats (top 5 features):")
    if hasattr(scaler, "mean_"):
        for i in range(5):
            print(f"  Feature {i}: Mean = {scaler.mean_[i]:.4f}, StdDev = {np.sqrt(scaler.var_[i]):.4f}")

def inspect_email_model():
    print("\n" + "=" * 60)
    print("EMAIL CLASSIFIER DIAGNOSTICS")
    print("=" * 60)
    
    if not os.path.exists(EMAIL_MODEL_PATH) or not os.path.exists(EMAIL_VEC_PATH):
        print("Email model or TF-IDF vectorizer files are missing in models/ directory.")
        return
        
    model = joblib.load(EMAIL_MODEL_PATH)
    vec = joblib.load(EMAIL_VEC_PATH)
    
    print(f"Model Class:      {type(model).__name__}")
    print(f"Vectorizer Class: {type(vec).__name__}")
    
    # Print model params
    if hasattr(model, "get_params"):
        params = model.get_params()
        print("\nHyperparameters:")
        for k in ['C', 'kernel', 'probability', 'random_state']:
            if k in params:
                print(f"  {k}: {params[k]}")
                
    # Vectorizer stats
    if hasattr(vec, "get_feature_names_out"):
        vocab = vec.get_feature_names_out()
        print(f"\nVocabulary Size:  {len(vocab)} unique words/tokens")
        print("Sample Vocabulary Tokens (first 10):")
        print("  ", list(vocab[:10]))

if __name__ == "__main__":
    inspect_url_model()
    inspect_email_model()
