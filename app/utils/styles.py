def inject_global_css():
    import streamlit as st
    st.markdown("""
    <style>
    /* ── Google Fonts ──────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;600;700;800&family=DM+Sans:ital,wght@0,400;0,500;0,600;1,400&family=Fira+Code:wght@400;500;600&display=swap');

    /* ── Root & body ───────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
    }
    .stApp {
        background-color: #090D16 !important;
        color: #94A3B8 !important;
    }

    /* Hide Streamlit footer & menu ─────────────────────────────── */
    #MainMenu  { display: none !important; }
    footer     { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }

    /* ── Block container width ──────────────────────────────────── */
    .block-container {
        max-width: 1050px !important;
        padding: 2.5rem 2rem 4rem !important;
    }

    /* ── Sidebar ────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: #0E1424 !important;
        border-right: 1px solid #1D263B !important;
    }
    [data-testid="stSidebar"] * { color: #8F9CAE !important; }
    [data-testid="stSidebar"] a { font-family: 'Syne', sans-serif !important; font-weight: 500 !important; }

    /* ── Top bar ────────────────────────────────────────────────── */
    [data-testid="stHeader"] {
        background: #090D16 !important;
        border-bottom: 1px solid #1D263B !important;
    }

    /* ── Headings ───────────────────────────────────────────────── */
    h1, h2, h3, h4 {
        font-family: 'Syne', sans-serif !important;
        letter-spacing: -0.01em !important;
        color: #F8FAFC !important;
    }
    h1 { font-size: 2.1rem !important; font-weight: 700 !important; margin-bottom: 4px !important; }
    h2 { font-size: 1.45rem !important; font-weight: 600 !important; margin-bottom: 2px !important; }
    h3 { font-size: 1.1rem !important; font-weight: 600 !important; margin-bottom: 2px !important; }
    p  { font-size: 0.9rem !important; color: #64748B !important; line-height: 1.6 !important; }

    /* ── Divider ────────────────────────────────────────────────── */
    hr { border: none !important; border-top: 1px solid #1D263B !important; margin: 1.5rem 0 !important; }

    /* ── Text inputs ────────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background:    #0E1424 !important;
        border:        1px solid #1D263B !important;
        border-radius: 6px !important;
        color:         #F8FAFC !important;
        font-family:  'Fira Code', monospace !important;
        font-size:     0.88rem !important;
        padding:       12px 14px !important;
        transition:    border-color .15s, box-shadow .15s !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00F0FF !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(0,240,255,.12) !important;
    }
    /* Input labels */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stMultiSelect label,
    .stFileUploader label {
        color: #8F9CAE !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: .08em !important;
        font-family: 'Syne', sans-serif !important;
    }

    /* ── Primary button ─────────────────────────────────────────── */
    .stButton > button {
        background:    #0E1424 !important;
        color:         #00F0FF !important;
        border:        1px solid #00F0FF !important;
        border-radius: 6px !important;
        font-weight:   600 !important;
        font-size:     0.85rem !important;
        padding:       10px 22px !important;
        letter-spacing:.05em !important;
        text-transform: uppercase !important;
        transition:    background .15s, transform .1s !important;
        font-family:  'Syne', sans-serif !important;
    }
    .stButton > button:hover  { background: rgba(0,240,255,.08) !important; transform: translateY(-1px) !important; }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── Download button ────────────────────────────────────────── */
    .stDownloadButton > button {
        background:    transparent !important;
        color:         #8F9CAE !important;
        border:        1px solid #1D263B !important;
        border-radius: 6px !important;
        font-weight:   600 !important;
        font-size:     0.82rem !important;
        padding:       9px 18px !important;
        text-transform: uppercase !important;
        letter-spacing: .04em !important;
        font-family:   'Syne', sans-serif !important;
        transition:    background .15s, border-color .15s !important;
    }
    .stDownloadButton > button:hover {
        background: #0E1424 !important;
        border-color: #8F9CAE !important;
    }

    /* ── Tabs ───────────────────────────────────────────────────── */
    [data-baseweb="tab-list"] {
        background:    transparent !important;
        border-bottom: 1px solid #1D263B !important;
        gap:           8px !important;
    }
    [data-baseweb="tab"] {
        background:    transparent !important;
        color:         #475569 !important;
        font-size:     0.82rem !important;
        font-weight:   600 !important;
        padding:       10px 16px !important;
        text-transform: uppercase !important;
        letter-spacing: .05em !important;
        font-family:   'Syne', sans-serif !important;
        border-bottom: 2px solid transparent !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        color:         #00F0FF !important;
        border-bottom: 2px solid #00F0FF !important;
        background:    transparent !important;
    }
    [data-testid="stTabPanel"] { padding-top: 1.5rem !important; }

    /* ── Selectbox / multiselect ─────────────────────────────────── */
    [data-baseweb="select"] > div {
        background:    #0E1424 !important;
        border-color:  #1D263B !important;
        border-radius: 6px !important;
    }
    [data-baseweb="popover"] { background: #0E1424 !important; border: 1px solid #1D263B !important; }
    [data-baseweb="menu"]    { background: #0E1424 !important; }
    [role="option"]          { color: #CBD5E1 !important; font-family: 'Syne', sans-serif !important; }
    [role="option"]:hover    { background: #1D263B !important; }

    /* ── File uploader ───────────────────────────────────────────── */
    [data-testid="stFileUploadDropzone"] {
        background:    #0E1424 !important;
        border:        1px dashed #1D263B !important;
        border-radius: 8px !important;
    }

    /* ── Checkbox ────────────────────────────────────────────────── */
    .stCheckbox > label > span:first-child { color: #8F9CAE !important; font-size: .875rem !important; }

    /* ── Dataframe ───────────────────────────────────────────────── */
    [data-testid="stDataFrame"] > div {
        border:        1px solid #1D263B !important;
        border-radius: 8px !important;
        overflow:      hidden !important;
    }
    [data-testid="stDataFrame"] iframe { background: #090D16 !important; }

    /* ── Alerts ──────────────────────────────────────────────────── */
    [data-testid="stAlert"] {
        border-radius: 6px !important;
        font-size:     0.88rem !important;
        font-family:  'DM Sans', sans-serif !important;
        background-color: #0E1424 !important;
        border: 1px solid #1D263B !important;
    }

    /* ── Progress ────────────────────────────────────────────────── */
    .stProgress > div > div > div > div {
        background: #00F0FF !important;
    }

    /* ── Chat ────────────────────────────────────────────────────── */
    [data-testid="stChatMessage"] {
        background:    #0E1424 !important;
        border:        1px solid #1D263B !important;
        border-radius: 8px !important;
    }
    [data-testid="stChatInput"] > div {
        background:    #0E1424 !important;
        border:        1px solid #1D263B !important;
        border-radius: 8px !important;
    }
    [data-testid="stChatInput"] textarea {
        background:    transparent !important;
        color:         #F8FAFC !important;
    }

    /* ── Page link nav cards ─────────────────────────────────────── */
    [data-testid="stPageLink"] a {
        display:       block !important;
        background:    #0E1424 !important;
        border:        1px solid #1D263B !important;
        border-radius: 8px !important;
        padding:       16px 20px !important;
        text-decoration: none !important;
        transition:    border-color .15s, box-shadow .15s !important;
        margin-bottom: 12px !important;
    }
    [data-testid="stPageLink"] a:hover {
        border-color: #00F0FF !important;
        box-shadow:   0 0 0 2px rgba(0,240,255,.08) !important;
    }
    [data-testid="stPageLink"] p {
        font-size:   0.92rem !important;
        font-weight: 500 !important;
        color:       #F8FAFC !important;
        margin:      0 !important;
        font-family: 'Syne', sans-serif !important;
    }

    /* ── Custom CyberShield components ───────────────────────────── */
    .cs-card {
        background:    #0E1424;
        border:        1px solid #1D263B;
        border-radius: 8px;
        padding:       20px 24px;
        margin-bottom: 12px;
    }
    .cs-metric-value {
        font-family:  'Fira Code', monospace;
        font-size:     2.1rem;
        font-weight:   600;
        color:         #F8FAFC;
        line-height:   1.1;
    }
    .cs-metric-label {
        font-family:   'Syne', sans-serif;
        font-size:     0.7rem;
        font-weight:   600;
        color:         #64748B;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin-top:    6px;
    }
    .cs-verdict-threat {
        background:    rgba(239,68,68,.04);
        border:        1px solid rgba(239,68,68,.25);
        border-left:   3px solid #EF4444;
        border-radius: 6px;
        padding:       16px 20px;
    }
    .cs-verdict-threat .cs-verdict-title { color: #FCA5A5; font-family: 'Syne', sans-serif; }
    .cs-verdict-threat .cs-verdict-body  { color: #E2E8F0; }
    .cs-verdict-safe {
        background:    rgba(16,185,129,.04);
        border:        1px solid rgba(16,185,129,.25);
        border-left:   3px solid #10B981;
        border-radius: 6px;
        padding:       16px 20px;
    }
    .cs-verdict-safe .cs-verdict-title { color: #6EE7B7; font-family: 'Syne', sans-serif; }
    .cs-verdict-safe .cs-verdict-body  { color: #E2E8F0; }
    .cs-verdict-title {
        font-size:     0.75rem;
        font-weight:   700;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin-bottom: 4px;
    }
    .cs-verdict-body { font-size: .88rem; font-weight: 400; line-height: 1.5; }
    .cs-section-label {
        font-family:   'Syne', sans-serif;
        font-size:     0.72rem;
        font-weight:   600;
        text-transform: uppercase;
        letter-spacing: .08em;
        color:         #475569;
        margin-bottom: 8px;
    }
    .cs-badge {
        display:        inline-block;
        background:     rgba(244,63,94,.08);
        color:          #FB7185;
        border:         1px solid rgba(244,63,94,.2);
        border-radius:  4px;
        padding:        3px 9px;
        font-size:      0.78rem;
        font-family:   'Fira Code', monospace;
        margin:         2px 4px 2px 0;
    }
    .cs-conf-badge {
        display:        inline-block;
        background:     rgba(0,240,255,.06);
        color:          #00F0FF;
        border:         1px solid rgba(0,240,255,.2);
        border-radius:  4px;
        padding:        3px 9px;
        font-size:      0.78rem;
        font-family:   'Fira Code', monospace;
    }
    </style>
    """, unsafe_allow_html=True)
