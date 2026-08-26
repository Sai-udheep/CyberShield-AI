# 🛡️ CyberShield AI: Explainable Phishing & Threat Detection Platform

> **An Offline, Privacy-First Cybersecurity Analytics Platform powered by XGBoost, Linear SVM, SHAP (SHapley Additive exPlanations), and Streamlit.**

---

## 📌 Project Overview

**CyberShield AI** is an advanced, explainable cybersecurity threat detection research platform designed to detect malicious URLs and phishing emails without transmitting sensitive user data to external cloud APIs.

By leveraging machine learning models trained on structural URL features, lexical attributes, HTML DOM properties, and TF-IDF text representations, CyberShield AI provides real-time threat verdicts, confidence scores, interactive model benchmarks, and detailed SHAP feature attributions explaining *why* a particular input was flagged.

---

## 🚀 Can I Deploy This on Vercel?

### ⚠️ Short Answer: **No, Vercel is not recommended for Streamlit apps.**

#### Why Vercel is unsuitable for CyberShield AI:
1. **Streamlit Architecture**: Streamlit relies on persistent WebSockets and long-polling HTTP connections to handle reactive UI updates. Vercel is built for stateless, event-driven Serverless Functions.
2. **Bundle Size Limits**: Machine learning dependencies (`xgboost`, `scikit-learn`, `shap`, `matplotlib`, `pandas`, `joblib`) exceed Vercel's serverless package limit (~250 MB).
3. **Database State**: CyberShield AI uses local SQLite (`scans.db`) for scan history. Serverless environments wipe local filesystem changes after each request.

---

### 🌐 Recommended Free Deployment Platforms

| Platform | Difficulty | Best For | Link / Guide |
| :--- | :--- | :--- | :--- |
| **Streamlit Community Cloud** *(Recommended)* | ⭐ Easy | Native 1-click GitHub deployment | [share.streamlit.io](https://share.streamlit.io/) |
| **Hugging Face Spaces** | ⭐ Easy | Free ML app hosting with Streamlit SDK | [huggingface.co/spaces](https://huggingface.co/) |
| **Render** | ⭐⭐ Medium | Web Service (Docker or Native Python) | [render.com](https://render.com/) |
| **Railway / Koyeb** | ⭐⭐ Medium | Docker container hosting | [railway.app](https://railway.app/) |

#### 1-Click Deployment via Streamlit Community Cloud (Recommended):
1. Push this repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **"New App"** -> Select your repository, branch (`main`), and set **Main file path** to `app/main.py`.
4. Click **Deploy!**

---

## ⚙️ Architecture & Module Breakdown

CyberShield AI consists of **5 main interactive modules/pages**:

```
CyberShield AI
 ├── 1. URL Scanner         (XGBoost + SHAP Explainability + Feature Extraction)
 ├── 2. Email Scanner       (Linear SVM + TF-IDF Vectorizer + Keyword Attribution)
 ├── 3. Model Comparison    (Interactive Plotly Benchmarks across 10 ML Classifiers)
 ├── 4. Cyber Assistant     (Offline TF-IDF Vector Similarity Knowledge Base)
 └── 5. Scan History        (SQLite Database Logging, Filtering & CSV Export)
```

---

### 1️⃣ URL Scanner (`pages/1_URL_Scanner.py`)
* **Purpose**: Performs real-time static and deep lexical analysis of web links to classify them as **Phishing** or **Legitimate**.
* **How It Works**:
  * **Homograph & IP Pre-checks**: Scans URLs for Internationalized Domain Name (IDN) homograph attacks (e.g., Cyrillic characters visually spoofing Latin domain names) and raw IP hostnames.
  * **50 Feature Extractor (`app/utils/url_extractor.py`)**: Extracts 50 statistical indicators across URL length, domain length, character entropy, sub-domain count, obfuscation ratio, special character density, HTTPS flags, and optional deep HTML DOM features (iFrames, hidden fields, password fields, popup counts, submit form targets).
  * **Multi-Model Evaluation**:
    1. **Primary Model (XGBoost Ablated)**: 38-feature model stripped of domain/brand matching bias.
    2. **Weighted Ensemble**: Combines outputs from Ablated XGBoost, Full XGBoost, and TF-IDF URL sequence models.
    3. **Biased Model (XGBoost Full)**: 50-feature model including brand-similarity heuristics.
    4. **Alternative Model (TF-IDF Text)**: Evaluates URL string token patterns.
  * **Explainability (SHAP Plots)**: Generates horizontal bar charts displaying the exact SHAP values driving the verdict.
  * **PDF Export**: Generates downloadable threat audit reports via `fpdf2`.

---

### 2️⃣ Email Scanner (`pages/2_Email_Scanner.py`)
* **Purpose**: Classifies raw email text and subject lines as **Spam/Phishing** or **Ham (Legitimate)**.
* **How It Works**:
  * **Text Preprocessing**: Cleans input by normalizing text, stripping HTML markup, removing special noise, and tokenizing words.
  * **TF-IDF Vectorization**: Transforms email text into high-dimensional TF-IDF feature vectors (`tfidf_vectorizer.joblib`).
  * **Linear SVM Classifier**: Uses a Linear Support Vector Machine (`email_best_model.joblib`) calibrated for 100% precision on legitimate communications to prevent false positives.
  * **Trigger Keyword Attribution**: Inspects model decision function weights (`coef_`) for every word present in the email, highlighting specific suspicious triggers (e.g., *urgent*, *verify*, *account suspended*, *claim prize*).
  * **Batch Scanning**: Supports uploading multi-row CSV files for automated bulk email classification.

---

### 3️⃣ Model Comparison (`pages/3_Model_Comparison.py`)
* **Purpose**: Provides an empirical research benchmark comparing 10 machine learning classifiers evaluated during development.
* **How It Works**:
  * Loads metric logs (`models/comparison_metrics.json`).
  * Visualizes **Accuracy, Precision, Recall, F1-Score**, and **Inference Latency (ms/sample)** using interactive Plotly bar charts.
  * Benchmark Models Evaluated:
    * **URL Models**: Logistic Regression, Random Forest, XGBoost (Ablated & Full), SVM, MLP Classifier.
    * **Email Models**: Logistic Regression, Multinomial Naive Bayes, Linear SVM, XGBoost, Random Forest.
  * Highlights optimal model selection rationales based on maximum F1-score and minimal latency.

---

### 4️⃣ Cyber Assistant (`pages/4_Cyber_Assistant.py`)
* **Purpose**: An offline, privacy-focused security Q&A bot providing instant guidance on cybersecurity topics.
* **How It Works**:
  * Uses an offline JSON knowledge base (`app/data/kb.json`) containing curated security definitions, phishing indicators, and incident handling guidelines.
  * Vectorizes user queries using TF-IDF and computes cosine similarity metrics (`app/utils/kb_search.py`).
  * Returns exact or nearest relevant responses along with match confidence percentage badges without calling any external LLM APIs.

---

### 5️⃣ Scan History (`pages/5_Scan_History.py`)
* **Purpose**: Provides a persistent dashboard for managing, reviewing, and auditing past scans on the local machine.
* **How It Works**:
  * Interacts with a local SQLite database (`scans.db`) initialized via SQLAlchemy (`app/utils/database.py`).
  * Displays dynamic summary metrics: total scans, flagged threats, safe links, and overall threat percentage.
  * Supports real-time filtering by scan type (URL/Email), verdict (Phishing/Safe/Spam/Ham), and keyword search.
  * Allows exporting the filtered record set to a CSV file or wiping logs.

---

## 🔬 Research & Empirical Foundations

CyberShield AI was developed as a cybersecurity research project focusing on **Feature Ablation**, **Explainable AI (XAI)**, and **Classifier Optimization**:

1. **Feature Ablation Study**:
   * *Problem*: standard URL phishing models rely heavily on brand string matching (e.g., checking if `paypal` is in the URL), leading to high false positives on legitimate subdomains or false negatives on unseen brands.
   * *Solution*: An ablated model was trained by stripping brand-similarity attributes (`URLSimilarityIndex`, `DomainTitleMatchScore`), yielding a robust 38-feature classifier (`url_model_ablated.joblib`) that generalizes to novel phishing campaigns.

2. **Model Performance Summary**:
   * **URL Classification**: XGBoost achieved **99.97% F1-score** with sub-millisecond inference latency (~0.001 ms).
   * **Email Classification**: Linear SVM achieved **100.0% Precision** and **94.3% F1-score**, prioritizing zero misclassifications of legitimate emails.

3. **Explainable AI (XAI) Integration**:
   * Integrates TreeSHAP (`url_shap_explainer_ablated.joblib`) to break down black-box tree predictions into quantifiable additive feature contributions.

---

## 📚 References & Research Sources

The development and datasets behind CyberShield AI draw upon the following research literature and open-source tools:

1. **PhiUSIIL Phishing URL Dataset**:
   * *Prasad, A., & Chandra, S.* — Feature extraction methodologies for URL lexical, structural, and HTML DOM analysis.
2. **SHAP (SHapley Additive exPlanations)**:
   * *Lundberg, S. M., & Lee, S.-I. (2017)*. "A Unified Approach to Interpreting Model Predictions." *Advances in Neural Information Processing Systems (NeurIPS 30)*.
3. **Phishing Email Benchmark Datasets**:
   * Public Kaggle & SpamAssassin email collections used for TF-IDF feature extraction and SVM tuning.
4. **Core Libraries**:
   * [Streamlit](https://streamlit.io/) — Interactive Web Application Framework.
   * [XGBoost](https://xgboost.readthedocs.io/) — Gradient Boosting Framework.
   * [Scikit-Learn](https://scikit-learn.org/) — Machine Learning in Python.
   * [Plotly](https://plotly.com/python/) — Interactive Graphing Library.

---

## 🛠️ Local Installation & Running Guide

```powershell
# 1. Clone the repository
git clone https://github.com/your-username/CyberShield-AI.git
cd CyberShield-AI

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1   # Windows PowerShell

# 3. Install requirements
pip install -r requirements.txt

# 4. Launch the application
streamlit run app/main.py
```
