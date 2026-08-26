import os
import sys
from datetime import datetime
from fpdf import FPDF

# Append path to import correct directories if run stand-alone
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def sanitize_text(text):
    """Encodes text to latin-1, replacing unsupported characters to prevent FPDF crashes."""
    if not isinstance(text, str):
        text = str(text)
    return text.encode('latin-1', 'replace').decode('latin-1')

class CyberShieldReport(FPDF):
    def header(self):
        # Draw a slate-colored decorative block at the top
        self.set_fill_color(15, 23, 42) # Dark Slate #0F172A
        self.rect(0, 0, 210, 22, 'F')
        
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_y(6)
        self.cell(0, 10, 'CYBERSHIELD AI - SECURITY REPORT', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(12)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(148, 163, 184) # Slate-400
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Confidential - Automated Threat Diagnostics', align='C')

def generate_pdf_report(scan_type, input_data, prediction, confidence, risk_score, top_features=None, shap_image_path=None, all_results=None):
    """
    Generates a byte-array PDF threat report using fpdf2.
    """
    pdf = CyberShieldReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # 1. Summary Card / Threat Banner
    is_threat = prediction in ['Phishing', 'Spam']
    pdf.set_y(30)
    
    # Background card based on status
    if is_threat:
        pdf.set_fill_color(254, 242, 242) # Light Red
        pdf.set_draw_color(248, 113, 113) # Red border
        text_color = (220, 38, 38)        # Dark Red text
        verdict = f"MALICIOUS THREAT DETECTED ({prediction.upper()})"
    else:
        pdf.set_fill_color(240, 253, 250) # Light Green
        pdf.set_draw_color(45, 212, 191)  # Green border
        text_color = (13, 148, 136)       # Dark Green text
        verdict = f"VERIFIED SECURE ({prediction.upper()})"
        
    pdf.rect(10, 28, 190, 18, 'DF')
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(*text_color)
    pdf.set_y(32)
    pdf.cell(0, 10, sanitize_text(verdict), align='C', new_x="LMARGIN", new_y="NEXT")
    
    # 2. Metadata Table
    pdf.ln(12)
    pdf.set_text_color(15, 23, 42)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 6, "Scan Diagnostics Metadata", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(226, 232, 240) # Slate border
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font('helvetica', '', 9)
    # Print metadata lines
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(40, 6, "Scan Date & Time:")
    pdf.cell(0, 6, date_str, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(40, 6, "Scan Category:")
    pdf.cell(0, 6, f"{scan_type} Threat Analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(40, 6, "Threat Confidence:")
    pdf.cell(0, 6, f"{confidence * 100:.2f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(40, 6, "Risk Score:")
    pdf.cell(0, 6, f"{risk_score}/100", new_x="LMARGIN", new_y="NEXT")
    
    # Handle potentially long input text gracefully by wrapping it using multi_cell
    pdf.cell(0, 6, "Scanned Input:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', 'I', 9)
    
    # Check for Unicode domain characters (IDNs)
    has_non_ascii = any(ord(c) > 127 for c in input_data)
    if has_non_ascii and scan_type.startswith("URL"):
        from app.utils.url_extractor import to_punycode_url
        puny_url = to_punycode_url(input_data)
        pdf.multi_cell(0, 5, f"{puny_url} (IDN / Unicode Hostname)", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.multi_cell(0, 5, sanitize_text(input_data), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font('helvetica', '', 9)
    
    # 3. Features Attribution / Key Findings
    if top_features:
        pdf.ln(8)
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(0, 6, "Analysis Key Indicators & Features", new_x="LMARGIN", new_y="NEXT")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font('helvetica', '', 9)
        pdf.set_fill_color(248, 250, 252) # Slate-50 background for headers
        pdf.cell(90, 6, "Feature Indicator", border=1, fill=True)
        pdf.cell(50, 6, "Attribution Influence", border=1, fill=True)
        pdf.cell(50, 6, "Observed Value", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        
        # Display up to 5 main indicators
        for feat in top_features[:5]:
            name, shap_val, actual_val = feat[0], feat[1], feat[2]
            
            # Format display name
            display_name = name.replace("NoOf", "Count of ").replace("Has", "Contains ").replace("Is", "Is ")
            
            # Format attribution impact string
            impact = "High Threat (+)" if shap_val > 0.1 else "Moderate Threat (+)" if shap_val > 0 else "Benign (-)"
            
            pdf.cell(90, 6, sanitize_text(display_name), border=1)
            pdf.cell(50, 6, sanitize_text(f"{shap_val:+.4f} ({impact})"), border=1)
            pdf.cell(50, 6, sanitize_text(actual_val), border=1, new_x="LMARGIN", new_y="NEXT")
            
    # 4. Multi-Model Comparative Diagnostics (if all_results is passed)
    if all_results:
        pdf.ln(8)
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(0, 6, "Multi-Model Comparative Diagnostics", new_x="LMARGIN", new_y="NEXT")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font('helvetica', '', 9)
        pdf.set_fill_color(248, 250, 252) # Slate-50 headers
        pdf.cell(70, 6, "Classifier Model", border=1, fill=True)
        pdf.cell(40, 6, "Verdict", border=1, fill=True)
        pdf.cell(40, 6, "Risk Score", border=1, fill=True)
        pdf.cell(40, 6, "Consensus Weight", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        
        # Comparative rows
        rows = [
            ("Weighted Consensus (Ensemble)", all_results["ensemble"], "100% (Consensus)"),
            ("Model B: XGBoost (Ablated)", all_results["ablated"], "50% (Structural)"),
            ("Model C: TF-IDF Text", all_results["tfidf"], "30% (Textual)"),
            ("Model A: XGBoost (Full)", all_results["full"], "20% (Brand Whitelist)")
        ]
        
        for name, res_dict, weight in rows:
            pdf.cell(70, 6, sanitize_text(name), border=1)
            pdf.cell(40, 6, sanitize_text(res_dict["prediction"]), border=1)
            pdf.cell(40, 6, sanitize_text(f"{res_dict['risk_score']}/100"), border=1)
            pdf.cell(40, 6, sanitize_text(weight), border=1, new_x="LMARGIN", new_y="NEXT")
        
    # 4. Security Action Guidelines
    pdf.ln(8)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 6, "Recommended Safety Guidelines", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font('helvetica', '', 9)
    if is_threat:
        recommendations = [
            "DO NOT click any buttons, links, or download attachments from this source.",
            "DO NOT provide any personal credentials, API keys, or financial credentials.",
            "Report this threat vector immediately to your IT safety / SOC security department.",
            "Flag or blacklist the sender's domain/URL inside your security firewalls or mail server filters."
        ]
    else:
        recommendations = [
            "No high-severity threats were identified on this input parameter.",
            "Although classified as safe, exercise caution if the context of this input requests urgent action.",
            "Verify sender identity if any URLs redirect to a financial or administrative portal."
        ]
        
    for rec in recommendations:
        pdf.multi_cell(0, 5, sanitize_text(f"- {rec}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        
    # 5. Future Academic Recommendations / Security Roadmap
    pdf.ln(6)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 6, "Academic Research Roadmap & Diagnostics Notes", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font('helvetica', '', 9)
    diagnostics = [
        "A feature ablation study was conducted to decouple URLSimilarityIndex dependencies, ensuring zero brand-whitelist leakage.",
        "Future diagnostic layers will implement a Hybrid Ensemble Classifier merging soft-voting logits from XGBoost, TF-IDF, and deep sequential RNN models.",
        "Attribution vectors utilize local explainability (SHAP values) to map feature influence dynamically on every threat diagnostic cycle."
    ]
    for diag in diagnostics:
        pdf.multi_cell(0, 5, sanitize_text(f"- {diag}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        
    # Output PDF as bytearray
    return pdf.output()

if __name__ == "__main__":
    print("Testing PDF Generation...")
    sample_features = [
        ("IsHTTPS", -3.7292, 0.0),
        ("LineOfCode", -3.3136, 0.0),
        ("URLSimilarityIndex", +2.2074, 100.0)
    ]
    pdf_bytes = generate_pdf_report(
        scan_type="URL",
        input_data="http://phish-secure-login.com",
        prediction="Phishing",
        confidence=0.985,
        risk_score=95,
        top_features=sample_features
    )
    print(f"Generated PDF successfully. Size: {len(pdf_bytes)} bytes.")
