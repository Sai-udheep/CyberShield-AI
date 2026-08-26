import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.utils.kb_search import kb_engine
from app.utils.styles import inject_global_css

st.set_page_config(page_title="Cyber Assistant — CyberShield AI", layout="wide", initial_sidebar_state="collapsed")
inject_global_css()

st.markdown("## Cyber Assistant")
st.markdown("<p style='margin-top:-8px; color:#64748B;'>Ask any cybersecurity question. Answers are matched offline using TF-IDF vector similarity.</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Suggested questions
st.markdown("<div class='cs-section-label'>Suggested questions</div>", unsafe_allow_html=True)
suggestions = [
    "What is a phishing attack?",
    "How do I spot a fake URL?",
    "What is typosquatting?",
    "How does email spoofing work?",
]
s_cols = st.columns(len(suggestions))
for col, q in zip(s_cols, suggestions):
    if col.button(q, use_container_width=True):
        st.session_state.setdefault("chat_history", [])
        st.session_state["pending_query"] = q

st.markdown("<br>", unsafe_allow_html=True)

# Init chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content":
         "Hello! Ask me anything about phishing, spoofing, spam, or general security best practices. "
         "I'll find the closest match from my offline knowledge base."}
    ]

# Render history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("confidence", 0) > 0:
            st.markdown(f'<span class="cs-conf-badge">Match confidence: {msg["confidence"]}%</span>',
                        unsafe_allow_html=True)

# Handle suggestion-button injection OR typed input
user_input = st.chat_input("Ask a cybersecurity question…")
if "pending_query" in st.session_state:
    user_input = st.session_state.pop("pending_query")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Searching knowledge base…"):
        res = kb_engine.query(user_input)

    reply = {"role": "assistant", "content": res["answer"],
             "confidence": res["confidence"] if res["found"] else 0}
    st.session_state.chat_history.append(reply)
    with st.chat_message("assistant"):
        st.markdown(res["answer"])
        if res["found"]:
            st.markdown(f'<span class="cs-conf-badge">Match confidence: {res["confidence"]}%</span>',
                        unsafe_allow_html=True)
