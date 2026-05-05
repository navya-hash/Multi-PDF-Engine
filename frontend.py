import streamlit as st
from backend import process_pdfs, user_input

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocMind — PDF Q&A",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap');

/* ── Root theme ── */
:root {
    --bg:        #0d0f12;
    --panel:     #13161b;
    --border:    #232830;
    --accent:    #e8ff47;
    --accent2:   #47c8ff;
    --text:      #e8eaf0;
    --muted:     #5a6070;
    --user-bubble: #1a2235;
    --bot-bubble:  #151a12;
}

/* ── Global reset ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}

.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Top bar ── */
.topbar {
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    padding: 18px 36px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.topbar-logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.45rem;
    letter-spacing: -0.5px;
    color: var(--accent);
}
.topbar-sub {
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 2px;
}
.topbar-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--muted);
    margin: 0 8px;
}
.topbar-dot.active { background: var(--accent); box-shadow: 0 0 8px var(--accent); }

/* ── Two-column shell ── */
.shell {
    display: flex;
    height: calc(100vh - 65px);
    overflow: hidden;
}

/* ── Left panel ── */
.left-panel {
    width: 320px;
    min-width: 300px;
    background: var(--panel);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    padding: 28px 24px;
    gap: 20px;
    overflow-y: auto;
}
.panel-label {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 4px;
}
.upload-zone {
    border: 1.5px dashed var(--border);
    border-radius: 10px;
    padding: 28px 16px;
    text-align: center;
    transition: border-color 0.2s;
}
.upload-zone:hover { border-color: var(--accent); }
.upload-icon { font-size: 2rem; margin-bottom: 8px; }
.upload-hint {
    font-size: 0.72rem;
    color: var(--muted);
    line-height: 1.6;
}

/* File chips */
.file-chip {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #1c2028;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.78rem;
    color: var(--text);
    margin-bottom: 8px;
    word-break: break-all;
}
.file-chip-icon { font-size: 1rem; flex-shrink: 0; }
.file-chip-name { flex: 1; color: var(--accent2); }
.file-chip-size { color: var(--muted); font-size: 0.68rem; flex-shrink: 0; }

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    padding: 6px 12px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
}
.status-ready {
    background: rgba(232,255,71,0.1);
    border: 1px solid rgba(232,255,71,0.3);
    color: var(--accent);
}
.status-idle {
    background: rgba(90,96,112,0.15);
    border: 1px solid var(--border);
    color: var(--muted);
}
.status-processing {
    background: rgba(71,200,255,0.1);
    border: 1px solid rgba(71,200,255,0.3);
    color: var(--accent2);
}

/* ── Right panel ── */
.right-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Chat history area */
.chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 28px 36px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

/* Empty state */
.empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    color: var(--muted);
    text-align: center;
}
.empty-state-icon { font-size: 3rem; opacity: 0.4; }
.empty-state-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--muted);
}
.empty-state-sub { font-size: 0.76rem; line-height: 1.7; max-width: 320px; }

/* Chat bubbles */
.chat-row { display: flex; gap: 12px; align-items: flex-start; }
.chat-row.user { flex-direction: row-reverse; }

.avatar {
    width: 34px; height: 34px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    flex-shrink: 0;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
}
.avatar-user { background: var(--accent); color: #0d0f12; }
.avatar-bot  { background: #1e2a1a; color: var(--accent); border: 1px solid rgba(232,255,71,0.2); }

.bubble {
    max-width: 72%;
    padding: 14px 18px;
    border-radius: 12px;
    font-size: 0.85rem;
    line-height: 1.75;
}
.bubble-user {
    background: var(--user-bubble);
    border: 1px solid #2a3550;
    border-top-right-radius: 3px;
    color: var(--accent2);
}
.bubble-bot {
    background: var(--bot-bubble);
    border: 1px solid rgba(232,255,71,0.12);
    border-top-left-radius: 3px;
    color: var(--text);
}
.bubble-meta {
    font-size: 0.65rem;
    color: var(--muted);
    margin-top: 6px;
    text-align: right;
}
.bubble-bot .bubble-meta { text-align: left; }

/* ── Input bar ── */
.input-bar {
    border-top: 1px solid var(--border);
    padding: 18px 36px;
    background: var(--panel);
}

/* Streamlit widget overrides */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploader"] > div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
[data-testid="stFileDropzone"] {
    background: #1c2028 !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 10px !important;
    padding: 20px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileDropzone"]:hover {
    border-color: var(--accent) !important;
}
[data-testid="stFileDropzone"] p,
[data-testid="stFileDropzone"] span,
[data-testid="stFileDropzone"] small {
    color: var(--muted) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.76rem !important;
}

/* Text input */
[data-testid="stTextInput"] > div > div {
    background: #1c2028 !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    transition: border-color 0.2s !important;
}
[data-testid="stTextInput"] > div > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(232,255,71,0.08) !important;
}
[data-testid="stTextInput"] input {
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.88rem !important;
}

/* Buttons */
[data-testid="stButton"] > button {
    background: var(--accent) !important;
    color: #0d0f12 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.06em !important;
    padding: 10px 22px !important;
    transition: opacity 0.2s, transform 0.15s !important;
    cursor: pointer !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* Secondary button */
.sec-btn > button {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
}
.sec-btn > button:hover { color: var(--text) !important; border-color: var(--muted) !important; }

/* Spinner / info */
[data-testid="stSpinner"] { color: var(--accent2) !important; }
.stAlert { border-radius: 8px !important; font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

/* Divider */
hr { border-color: var(--border) !important; margin: 12px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Session state ───────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []          # list of {"role": "user"|"bot", "text": str}
if "processed" not in st.session_state:
    st.session_state.processed = False
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0

# ─── Top bar ────────────────────────────────────────────────────────────────
dot_class = "active" if st.session_state.processed else ""
st.markdown(f"""
<div class="topbar">
    <div>
        <div class="topbar-logo">⬡ DocMind</div>
        <div class="topbar-sub">Multi-PDF Intelligence Engine</div>
    </div>
    <div class="topbar-dot {dot_class}"></div>
    <div style="font-size:0.72rem; color:var(--muted); letter-spacing:0.1em; text-transform:uppercase;">
        {'Index Ready' if st.session_state.processed else 'No Index'}
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Two-column layout ────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 2.6], gap="small")

# ════════════════════════════════════════════════
# LEFT PANEL — Document Upload
# ════════════════════════════════════════════════
with left_col:
    st.markdown('<div class="panel-label">📂 Documents</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop PDF files here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    # File chips
    if uploaded_files:
        st.markdown("---")
        st.markdown('<div class="panel-label">Uploaded Files</div>', unsafe_allow_html=True)
        for f in uploaded_files:
            size_kb = round(f.size / 1024, 1)
            size_str = f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb/1024,1)} MB"
            st.markdown(f"""
            <div class="file-chip">
                <span class="file-chip-icon">📄</span>
                <span class="file-chip-name">{f.name}</span>
                <span class="file-chip-size">{size_str}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Status badge
    if st.session_state.processed:
        st.markdown(f"""
        <div class="status-badge status-ready">
            ✦ Index ready &nbsp;·&nbsp; {st.session_state.chunk_count} chunks
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-badge status-idle">
            ○ No index built yet
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Process button
    if uploaded_files:
        if st.button("⚡ Build Index", use_container_width=True):
            with st.spinner("Reading & embedding PDFs…"):
                try:
                    count = process_pdfs(uploaded_files)
                    st.session_state.processed = True
                    st.session_state.chunk_count = count
                    st.success(f"Done! {count} chunks indexed.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.markdown("""
        <div class="upload-hint" style="text-align:center; padding: 8px 0;">
            Upload one or more PDF files<br>then click <strong style="color:var(--accent)">Build Index</strong>
        </div>
        """, unsafe_allow_html=True)

    # Clear chat
    if st.session_state.chat_history:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="sec-btn">', unsafe_allow_html=True)
            if st.button("🗑 Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# RIGHT PANEL — Chat Interface

with right_col:

    # ── Chat history ──
    chat_container = st.container(height=520)
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-title">Ask anything about your documents</div>
                <div class="empty-state-sub">
                    Upload PDFs on the left, build the index,<br>
                    then type your question below.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-row user">
                        <div class="avatar avatar-user">U</div>
                        <div>
                            <div class="bubble bubble-user">{msg["text"]}</div>
                            <div class="bubble-meta">You</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-row">
                        <div class="avatar avatar-bot">AI</div>
                        <div>
                            <div class="bubble bubble-bot">{msg["text"]}</div>
                            <div class="bubble-meta">DocMind</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── Input bar ──
    st.markdown("---")
    input_col, btn_col = st.columns([5, 1], gap="small")

    with input_col:
        question = st.text_input(
            "question",
            placeholder="Ask a question about your documents…",
            label_visibility="collapsed",
            key="question_input",
            disabled=not st.session_state.processed,
        )

    with btn_col:
        ask_btn = st.button(
            "Ask →",
            use_container_width=True,
            disabled=not st.session_state.processed,
        )

    if not st.session_state.processed:
        st.markdown("""
        <div style="font-size:0.72rem; color:var(--muted); margin-top:6px;">
            ← Build the document index first to enable Q&amp;A
        </div>
        """, unsafe_allow_html=True)

    # ── Handle question submission ──
    if ask_btn and question.strip():
        st.session_state.chat_history.append({"role": "user", "text": question.strip()})
        with st.spinner("Thinking…"):
            try:
                answer = user_input(question.strip())
                st.session_state.chat_history.append({"role": "bot", "text": answer})
            except Exception as e:
                st.session_state.chat_history.append({
                    "role": "bot",
                    "text": f"Error generating response: {e}"
                })
        st.rerun()