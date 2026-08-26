# Literature Review: Email Spam & Phishing Detection Models

This literature review analyzes five research papers located in the `research/` folder. These papers cover machine learning and deep learning methodologies for detecting email spam, phishing URLs, and phishing websites. In addition, the corresponding [literature_review.xlsx](file:///d:/CyberShield-AI/research/literature_review.xlsx) has been updated with these details.

---

## 1. Executive Summary

The reviewed literature represents three key areas in cybersecurity threat classification:
1. **Email Spam Detection**: Focused on content classification using text representation (TF-IDF, NLP, and BERT transformer embeddings) coupled with classifiers (SVMs, Naive Bayes, Random Forests).
2. **Phishing URL Detection**: Classifying links directly based on lexical syntax and structural indicators (length, subdomain count, SSL states).
3. **Phishing Website Detection**: Deep content and meta-analysis of webpage structures (HTML properties, anchor links, external forms) using deep neural architectures (Bi-LSTMs, CNNs) combined with explainability frameworks (SHAP) to improve detection transparency.

---

## 2. Detailed Paper Reviews

### 1. An Efficient Email Spam Detection Framework Using TF-IDF and Comparative ML (2026)
* **Author**: Mrs. R. Mano Ranjani, Gandu Eshwar, Chirra Ram Gopal Rao, Thandu Venkat Sai
* **Domain**: Email Spam Filtering
* **Dataset**: SpamAssassin Corpus (5,572 messages: 4,516 ham, 1,056 spam; 81/19% class split).
* **Feature Engineering**: Standard text cleaning pipeline: tokenization, lowercase conversion, stop-word removal, and Porter stemming. TF-IDF vectorization was limited to the 3,000 most frequent tokens to mitigate feature space sparsity.
* **Methodology**: Evaluated 11 supervised classifiers (SVC, LinearSVC, KNN, MNB, Decision Tree, Logistic Regression, Random Forest, AdaBoost, Bagging Classifier, Extra Trees, Gradient Boosting, XGBoost) and two ensembles (Soft Voting and Stacking).
* **Key Findings**:
  - The proposed **Linear SVM** pipeline achieved **98.2% test accuracy** (99.9% training accuracy), exhibiting low overfitting despite high feature dimensionality.
  - **Extra Trees Classifier (ETC)** achieved the highest individual tree classifier accuracy at **97.87%**.
  - **Multinomial Naive Bayes (MNB)**, **Random Forest (RF)**, and **KNN** reached **100% Precision**, eliminating critical false positives.
  - The **Voting Classifier** (SVC + MNB + ETC) combined high accuracy (98.16%) with perfect precision (100%).
* **Limitations**: 
  - TF-IDF cannot capture context or inter-word semantic relationships.
  - The framework is purely text-based, making it vulnerable to image spam, styling obfuscations, and multi-hop URL redirects.
  - Heavy ensemble models (Stacking, Gradient Boosting) introduce substantial inference latency.

---

### 2. Machine Learning Algorithm for Detecting Suspicious Email Messages Using NLP (2025)
* **Author**: Ghadah Alkhodhairy, Kashif Saleem (King Saud University)
* **Domain**: Email Phishing & Threat Detection
* **Dataset**: Kaggle Email Spam Classification Dataset (5,172 emails: 39.4% spam/phishing, 60.6% non-spam).
* **Feature Engineering**: Explores text-based features under four modes: One-Hot encoding, TF-IDF Vectorization, BERT contextual embeddings, and a Combined vector (One-Hot + TF-IDF + BERT).
* **Methodology**: Proposes a **Support Vector Classifier (SVC)** utilizing Radial Basis Function (RBF) kernel and GridSearchCV hyperparameter tuning. Baseline models include Random Forest, ANN, Decision Tree, and Naive Bayes. Oversampling (SMOTE) and class-weight adjustments were applied to manage class imbalance.
* **Key Findings**:
  - **Proposed SVC + Combined features** model achieved **98.65% Accuracy** (98.52% Precision, 99.59% Recall, 99.05% F1-score), outperforming the baseline classifiers.
  - Table 1 shows **Combined features** alone achieved **99.35% Accuracy** (BERT alone reached 99.10%, TF-IDF reached 97.50%, and One-Hot reached 95.85%).
  - Integrating SMOTE oversampling improved recall from 99.59% to 99.75%, significantly reducing false negatives.
* **Limitations**:
  - High computational overhead of BERT embeddings (proposed model takes 42.1s training time, uses 120MB memory, and has a 3.2ms/email inference latency).
  - Benchmark template biases and lack of real-world metadata (sender IP, domain reputation, organizational hierarchy) limit generalizability.
  - Primary testing restricted to English-language corpora.

---

### 3. PhiUSIIL Phishing URL Detection: A Comprehensive Statistical Analysis (2026)
* **Author**: Patrick Muthii
* **Domain**: Phishing URL Classification
* **Dataset**: PhiUSIIL Phishing URL Dataset (235,795 URLs: 134,850 legitimate, 100,945 phishing; 57/43% split). Legitimate URLs sourced from OpenPageRank, and phishing links from PhishTank, OpenPhish, and MalwareWorld.
* **Feature Engineering**: 46 distinct features divided into:
  - *URL-based features*: Length, domain length, URL similarity index, char continuation rate, TLD legitimate probability, HTTPS status, etc.
  - *Webpage content features*: Line of code, Has Title, Robots, Is Responsive, redirection counts, hidden/password fields, financial keywords (Bank, Pay, Crypto), copyright/social network tags, etc.
* **Methodology**: Evaluated Random Forest, Decision Tree, and Logistic Regression models. Uses statistical verification (Mann-Whitney U and Chi-Square tests).
* **Key Findings**:
  - **Random Forest** and **Decision Tree** models achieved **near-perfect performance (100% metrics across the board)** on test data, while Logistic Regression reached 99.99% accuracy.
  - **URL Similarity Index** was consistently ranked as the single most predictive feature across all algorithms.
  - Statistical analysis proved that phishing URLs are significantly longer, have complex subdomains, and use obscure character ratios.
* **Limitations**:
  - High risk of overfitting. Perfect metrics strongly suggest model leakage or dataset-specific separations that may not hold on live traffic.
  - No external validation datasets were evaluated.
  - Static evaluation of webpage structural tags, which attackers can quickly obfuscate.

---

### 4. AI-Driven Phishing Website Detection Using Machine Learning (2025)
* **Author**: Kajal Nitin Bauskar (GIMR, Jalgaon)
* **Domain**: Phishing URL & Domain Classification
* **Dataset**: Balanced Dataset of 11,500 URLs (50/50% split) collected from PhishTank, OpenPhish, and trusted domain lists.
* **Feature Engineering**: Features categorized into:
  - *Lexical*: URL/domain length, subdomains, special characters, entropy, and keywords (login, verify, update).
  - *Security*: HTTPS/SSL certificate presence, redirections, URL shortening.
  - *Host-Based*: Domain age, expiration status, DNS record validation, IP-based domains.
* **Methodology**: Evaluated LightGBM, XGBoost, Random Forest, Gradient Boosting, SVM, Decision Tree, and Logistic Regression.
* **Key Findings**:
  - **LightGBM** achieved the highest accuracy at **99.81%**, outperforming XGBoost (99.74%) and Random Forest (98.62%).
  - LightGBM's leaf-wise tree growth enabled rapid processing of high-dimensional URL attributes, demonstrating robust classification against obfuscations.
* **Limitations**:
  - Operates purely on URL lexical metadata; does not analyze real-time page content.
  - Lacks integration with client-side agents (such as browser extensions).
  - Does not account for domain popularity or traffic metrics.

---

### 5. SHAP-based Interpretable Deep Learning Framework for Phishing Website Detection (2025)
* **Author**: Rizki Wahyudi et al.
* **Domain**: Phishing Website Detection & Explainable AI (XAI)
* **Dataset**: UCI Phishing Websites Dataset (11,055 records; 75/25% stratified train/test split).
* **Feature Engineering**: URL and webpage content attributes (e.g. URL of Anchor, SSL State, Prefix/Suffix hyphens, Subdomain presence, Request URL redirects, iframe blocks, right-click disabling).
* **Methodology**: Benchmarked five deep architectures (ANN, MLP, Autoencoder, CNN, Bi-LSTM). Implemented **SHAP (Shapley Additive Explanations)** (via DeepSHAP and KernelSHAP) to extract local and global feature attribution.
* **Key Findings**:
  - **Bi-LSTM** achieved the best overall performance: **97.03% Accuracy** (96.31% Precision, 98.44% Recall, 97.36% F1-score, and 0.993 ROC-AUC).
  - SHAP analysis identified **URL_of_Anchor** (proportion of anchor links pointing to external/suspicious domains) and **SSLfinal_State** (validity of SSL certificate) as the two most dominant features driving predictions.
  - Bi-LSTM provided the most stable, domain-aligned feature attributions, while CNN focused on localized kernel-driven spatial structures.
* **Limitations**:
  - Bi-LSTM's temporal sequence structure introduces significant computational and inference overhead, limiting real-time streaming scalability.
  - Static UCI Phishing Websites dataset lacks representation of modern evasion strategies.
  - High dependency on clean, labeled representation datasets.

---

## 3. Comparison Matrix of Literature

| Paper # | Topic / Domain | Dataset Description | Key Features | Evaluated Models | Best Performing Model & Performance | Major Limitations / Gaps |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Email Spam Detection | SpamAssassin (5,572 messages; 81% ham, 19% spam) | TF-IDF (3,000 top vocabulary terms after tokenization, stemming) | Linear SVM, SVC, KNN, MNB, DT, RF, AdaBoost, Stacking, Voting | **Extra Trees** (97.87% Acc), **Linear SVM** (98.2% test Acc), **Voting** (98.16% Acc, 100% Precision) | No semantic/contextual understanding; easily bypassed by image-based spam and complex redirects. |
| **2** | Suspicious Emails | Kaggle Dataset (5,172 emails; 39.4% spam, 60.6% ham) | One-Hot, TF-IDF, BERT embeddings, Combined | SVC (Proposed), RF, ANN, DT, Naive Bayes, Gradient Boosting | **SVC + Combined Features** (98.65% Acc, 98.52% Prec, 99.59% Rec, 99.05% F1) | High BERT latency (3.2 ms/email, 42.1s training); lacks metadata (IP, sender history); English only. |
| **3** | Phishing URLs | PhiUSIIL (235,795 URLs; 57% leg, 43% phish) | 46 features: Lexical URL, HTML structure (Line of Code, hidden fields) | Random Forest, Decision Tree, Logistic Regression | **Random Forest** (100% metrics across the board, 1.0 AUC), **Logistic Reg.** (99.99% Acc) | Extremely high overfitting risk; dataset-specific separability; no external validation. |
| **4** | Phishing URLs | Balanced URLs (11,500 URLs; 50% leg, 50% phish) | Lexical (Length, subdomains), Security (SSL, shortening), Host-based (DNS, age) | LightGBM, XGBoost, Random Forest, SVM, Decision Tree, Logistic Regression | **LightGBM** (99.81% Acc), **XGBoost** (99.74% Acc), **Random Forest** (98.62% Acc) | No real-time HTML content analysis; no browser agent integration; does not track domain popularity. |
| **5** | Phishing Websites | UCI Phishing Websites (11,055 records; 75/25 split) | URL and page structure (Anchor URL, SSLFinal state, redirect counts) | ANN, MLP, Autoencoder, CNN, Bi-LSTM + SHAP (XAI) | **Bi-LSTM** (97.03% Acc, 96.31% Prec, 98.44% Rec, 97.36% F1, 0.993 ROC-AUC) | Bi-LSTM computational complexity limits real-time streaming; benchmark is static; English-centric. |

---

## 4. Key Takeaways for CyberShield-AI

When building the **CyberShield-AI** defensive system, we should draw upon several key architectural paradigms identified in this literature review:

1. **Feature Fusion (Linguistic + Contextual + Structural)**:
   * As shown in Paper 2, combining simple keyword representations (TF-IDF) with rich semantic contexts (BERT embeddings) and metadata (One-Hot encoded sender/recipient headers) yields the most robust defense against modern obfuscated emails.
   
2. **Real-time vs Asynchronous Architectures**:
   * For inline, real-time protection (e.g., mail processing gateways or client extensions), lightweight models like **Linear SVM** (Paper 1) or **LightGBM** (Paper 4) are optimal due to low inference latencies (sub-millisecond to 3.2 ms).
   * Heavy models (like **Bi-LSTM** or **BERT** pipelines) are best deployed as asynchronous, secondary scanning layers to analyze high-risk or flagged assets.

3. **Operational Optimization (Precision vs Recall)**:
   * In email filtering, **Precision** is paramount because misclassifying a legitimate business email (false positive) is more costly than letting a spam message pass. Soft voting ensembles (Paper 1) or threshold tuning can fully eliminate false positives.
   * In website blocklists, **Recall** is prioritized to catch dangerous credentials-harvesting pages, meaning models like Bi-LSTM (Paper 5) are preferred.

4. **Explainability & Transparency (SHAP)**:
   * Integrating SHAP (Paper 5) transforms a model from a "black box" into an auditable intelligence tool. Security analysts can trace exactly why a URL was flagged (e.g., due to an anomalous `URL_of_Anchor` or missing `SSLfinal_State`).

5. **Evasion Mitigation**:
   * Attackers routinely bypass static signatures. Future-proofing CyberShield-AI requires checking domain age, certificate validity, redirection paths, and page structure rather than relying solely on text or static blacklists.
