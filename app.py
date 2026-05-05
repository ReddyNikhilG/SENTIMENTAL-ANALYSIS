from __future__ import annotations

from collections import Counter
from datetime import datetime
from io import StringIO
import csv
import re
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st
from pypdf import PdfReader
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(
    page_title="Sentiment Studio",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

THEME_TOKENS: dict[str, dict[str, str]] = {
    "dark": {
        "app_background": "radial-gradient(circle at top left, rgba(255, 255, 255, 0.06), transparent 26%), radial-gradient(circle at top right, rgba(148, 163, 184, 0.06), transparent 22%), linear-gradient(180deg, #000000 0%, #050505 48%, #0a0a0a 100%)",
        "surface": "rgba(15, 15, 15, 0.92)",
        "surface_soft": "rgba(20, 20, 20, 0.74)",
        "surface_alt": "rgba(255, 255, 255, 0.05)",
        "border": "rgba(148, 163, 184, 0.18)",
        "text_main": "#e5eefb",
        "text_sub": "#cbd5e1",
        "muted": "#94a3b8",
        "accent": "#38bdf8",
        "accent_2": "#60a5fa",
        "accent_soft": "rgba(56, 189, 248, 0.15)",
        "chip_bg": "rgba(15, 23, 42, 0.55)",
        "input_bg": "rgba(15, 23, 42, 0.75)",
    },
    "light": {
        "app_background": "radial-gradient(circle at top left, rgba(14, 165, 233, 0.14), transparent 28%), radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 24%), linear-gradient(180deg, #f7fbff 0%, #edf4fb 52%, #e7eef8 100%)",
        "surface": "rgba(255, 255, 255, 0.88)",
        "surface_soft": "rgba(248, 250, 252, 0.78)",
        "surface_alt": "rgba(15, 23, 42, 0.05)",
        "border": "rgba(148, 163, 184, 0.28)",
        "text_main": "#0f172a",
        "text_sub": "#334155",
        "muted": "#64748b",
        "accent": "#0284c7",
        "accent_2": "#0f766e",
        "accent_soft": "rgba(2, 132, 199, 0.12)",
        "chip_bg": "rgba(255, 255, 255, 0.72)",
        "input_bg": "rgba(255, 255, 255, 0.9)",
    },
}


def inject_styles(theme: str) -> None:
    tokens = THEME_TOKENS[theme]
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {tokens['app_background']};
            color: {tokens['text_main']};
            font-family: "Space Grotesk", "Segoe UI", sans-serif;
            --text-main: {tokens['text_main']};
            --text-sub: {tokens['text_sub']};
            --text-muted: {tokens['muted']};
            --surface: {tokens['surface']};
            --surface-soft: {tokens['surface_soft']};
            --surface-alt: {tokens['surface_alt']};
            --surface-border: {tokens['border']};
            --accent: {tokens['accent']};
            --accent-2: {tokens['accent_2']};
            --accent-soft: {tokens['accent_soft']};
            --chip-bg: {tokens['chip_bg']};
            --input-bg: {tokens['input_bg']};
        }}

        .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }}

        .theme-shell {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
            padding: 0.8rem 1rem;
            border: 1px solid var(--surface-border);
            border-radius: 18px;
            background: var(--surface-soft);
            box-shadow: 0 18px 44px rgba(2, 6, 23, 0.10);
        }}

        .theme-label {{
            font-size: 0.78rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 0.25rem;
        }}

        .theme-title {{
            font-size: 1rem;
            font-weight: 700;
            color: var(--text-main);
        }}

        .hero {{
            padding: 1.8rem;
            border: 1px solid var(--surface-border);
            border-radius: 26px;
            background: linear-gradient(180deg, var(--surface), var(--surface-soft));
            box-shadow: 0 22px 60px rgba(2, 6, 23, 0.18);
        }}

        .hero-grid {{
            display: grid;
            grid-template-columns: 1.3fr 0.9fr;
            gap: 1rem;
            align-items: stretch;
        }}

        .hero-panel {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.75rem;
        }}

        .hero-stat {{
            border-radius: 20px;
            padding: 1rem;
            border: 1px solid var(--surface-border);
            background: var(--surface-alt);
        }}

        .hero-stat .label {{
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-size: 0.72rem;
            color: var(--text-muted);
        }}

        .hero-stat .value {{
            margin-top: 0.35rem;
            font-size: 1.7rem;
            font-weight: 700;
            color: var(--text-main);
        }}

        .hero-stat .note {{
            margin-top: 0.2rem;
            color: var(--text-sub);
            font-size: 0.85rem;
        }}

        .hero-cta {{
            display: flex;
            gap: 0.65rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }}

        .eyebrow, .section-kicker {{
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.72rem;
            color: var(--accent);
            margin-bottom: 0.45rem;
        }}

        .hero h1 {{
            font-size: clamp(2.2rem, 4vw, 4.2rem);
            margin: 0;
            line-height: 0.98;
            color: var(--text-main);
        }}

        .hero p {{
            margin: 0.85rem 0 0;
            color: var(--text-sub);
            max-width: 72ch;
            font-size: 1.02rem;
        }}

        .chip-row, .action-row {{
            display: flex;
            gap: 0.65rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }}

        .chip, .tool-chip {{
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.42rem 0.78rem;
            border: 1px solid var(--surface-border);
            background: var(--chip-bg);
            color: var(--text-main);
            font-size: 0.82rem;
        }}

        .card {{
            border: 1px solid var(--surface-border);
            border-radius: 24px;
            background: linear-gradient(180deg, var(--surface), var(--surface-soft));
            padding: 1.2rem;
            box-shadow: 0 18px 45px rgba(2, 6, 23, 0.12);
        }}

        .metric-card {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin-top: 1rem;
        }}

        .metric {{
            border-radius: 18px;
            padding: 1rem;
            background: var(--surface-alt);
            border: 1px solid var(--surface-border);
        }}

        .metric-label {{
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: var(--text-muted);
        }}

        .metric-value {{
            font-size: 1.7rem;
            font-weight: 700;
            margin-top: 0.25rem;
            color: var(--text-main);
        }}

        .metric-note {{
            margin-top: 0.3rem;
            color: var(--text-sub);
            font-size: 0.85rem;
        }}

        .result-positive {{ color: #22c55e; }}
        .result-negative {{ color: #ef4444; }}
        .result-neutral {{ color: #eab308; }}

        .stTextArea textarea {{
            background: var(--input-bg) !important;
            color: var(--text-main) !important;
            border: 1px solid var(--surface-border) !important;
            border-radius: 16px !important;
            min-height: 190px;
        }}

        .section-title {{
            margin: 0 0 0.75rem;
            font-size: 1.15rem;
            color: var(--text-main);
        }}

        .footer-note {{
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 1rem;
        }}

        .upload-card {{
            margin-top: 1rem;
            padding: 1rem;
            border-radius: 18px;
            border: 1px dashed var(--surface-border);
            background: linear-gradient(180deg, var(--surface-soft), var(--surface-alt));
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.9rem;
        }}

        .chart-card {{
            min-height: 0;
            padding: 1rem;
        }}

        .chart-stack {{
            display: grid;
            gap: 0.5rem;
        }}

        .chart-stack .chart-card {{
            min-height: 0;
        }}

        .chart-stack .stAlert {{
            margin: 0.35rem 0 0;
        }}

        .chart-stack .stAltairChart, .chart-stack [data-testid="stVerticalBlockBorderWrapper"] {{
            margin-top: 0.15rem;
        }}

        .pdf-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            margin-top: 0.5rem;
            padding: 0.42rem 0.7rem;
            border-radius: 999px;
            background: var(--accent-soft);
            border: 1px solid var(--surface-border);
            color: var(--text-main);
            font-size: 0.8rem;
        }}

        .small-note {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
        }}

        .feature-card {{
            border-radius: 22px;
            padding: 1rem;
            border: 1px solid var(--surface-border);
            background: linear-gradient(180deg, var(--surface), var(--surface-alt));
        }}

        .feature-card h4 {{
            margin: 0 0 0.35rem;
            font-size: 1rem;
            color: var(--text-main);
        }}

        .feature-card p {{
            margin: 0;
            color: var(--text-sub);
            line-height: 1.55;
            font-size: 0.93rem;
        }}

        .pipeline {{
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 0.65rem;
        }}

        .step-card {{
            border-radius: 18px;
            padding: 0.95rem;
            border: 1px solid var(--surface-border);
            background: var(--surface-alt);
            min-height: 130px;
        }}

        .step-index {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            background: var(--accent-soft);
            color: var(--text-main);
            font-weight: 700;
            margin-bottom: 0.6rem;
        }}

        .step-card h4 {{
            margin: 0 0 0.35rem;
            font-size: 0.95rem;
        }}

        .step-card p {{
            margin: 0;
            color: var(--text-sub);
            font-size: 0.9rem;
            line-height: 1.45;
        }}

        .tech-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
        }}

        .cta-band {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        @media (max-width: 920px) {{
            .metric-card, .chart-grid {{
                grid-template-columns: 1fr 1fr;
            }}

            .hero-grid, .feature-grid, .pipeline {{
                grid-template-columns: 1fr 1fr;
            }}

            .theme-shell {{
                flex-direction: column;
                align-items: stretch;
            }}
        }}

        @media (max-width: 640px) {{
            .metric-card, .chart-grid, .hero-grid, .feature-grid, .pipeline {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

ANALYZER = SentimentIntensityAnalyzer()
MAX_HISTORY = 50
MAX_CHARS = 5000

SAMPLE_TEXTS = {
    "Positive sample": "The product quality is excellent and support was very helpful.",
    "Negative sample": "The app keeps crashing and the experience is frustrating.",
    "Neutral sample": "The service is okay, but there is room for improvement.",
}

MODEL_NAME = "VADER Sentiment Analyzer"
MODEL_DESCRIPTION = (
    "A lightweight rule-based sentiment engine that is fast to deploy on Streamlit Cloud. "
    "It scores text into positive, negative, or neutral sentiment and converts the score into a 0-4 scale."
)
MODEL_TECH = "vaderSentiment"

STOPWORDS = {
    "the",
    "is",
    "a",
    "an",
    "and",
    "to",
    "for",
    "of",
    "it",
    "this",
    "that",
    "was",
    "with",
    "but",
    "are",
    "in",
    "on",
    "at",
    "be",
    "as",
    "or",
    "by",
    "from",
    "we",
    "you",
    "they",
    "i",
    "me",
    "my",
    "our",
    "your",
}


def ensure_state() -> None:
    defaults = {
        "current_text": "",
        "current_result": None,
        "history": [],
        "error": "",
        "ui_theme": "dark",
        "pdf_text": "",
        "pdf_names": [],
        "last_pdf_signature": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def classify(compound: float) -> tuple[str, int, str]:
    if compound >= 0.05:
        return "Positive", min(4, round((compound + 1.0) * 2.0)), "😊"
    if compound <= -0.05:
        return "Negative", max(0, min(4, round((compound + 1.0) * 2.0))), "😡"
    return "Neutral", 2, "😐"


def analyze_text(text: str) -> dict[str, Any]:
    scores = ANALYZER.polarity_scores(text)
    sentiment, score, emoji = classify(scores["compound"])
    confidence = max(scores["pos"], scores["neg"], scores["neu"])
    return {
        "text": text,
        "sentiment": sentiment,
        "score": score,
        "emoji": emoji,
        "confidence": confidence,
        "confidence_text": f"{round(confidence * 100)}%",
        "compound": scores["compound"],
        "pos": scores["pos"],
        "neg": scores["neg"],
        "neu": scores["neu"],
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    }


def push_history(record: dict[str, Any]) -> None:
    history = [record, *st.session_state.history]
    st.session_state.history = history[:MAX_HISTORY]


def export_history_csv(history: list[dict[str, Any]]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=["created_at", "sentiment", "score", "emoji", "confidence_text", "text"],
    )
    writer.writeheader()
    for item in history:
        writer.writerow(
            {
                "created_at": item["created_at"],
                "sentiment": item["sentiment"],
                "score": item["score"],
                "emoji": item["emoji"],
                "confidence_text": item["confidence_text"],
                "text": item["text"],
            }
        )
    return buffer.getvalue()


def top_terms(history: list[dict[str, Any]]) -> pd.DataFrame:
    joined = " ".join(item["text"] for item in history).lower()
    tokens = re.findall(r"[a-z]+", joined)
    counts = Counter(token for token in tokens if len(token) > 2 and token not in STOPWORDS)
    if not counts:
        counts = Counter({"sentiment": 18, "analysis": 14, "insight": 12})
    top = counts.most_common(12)
    return pd.DataFrame(top, columns=["word", "count"])


def sentiment_badge_class(sentiment: str) -> str:
    if sentiment == "Positive":
        return "result-positive"
    if sentiment == "Negative":
        return "result-negative"
    return "result-neutral"


def extract_pdf_text(uploaded_files: list[Any]) -> tuple[str, list[str]]:
    texts: list[str] = []
    names: list[str] = []

    for uploaded_file in uploaded_files:
        try:
            reader = PdfReader(uploaded_file)
            page_text = [page.extract_text() or "" for page in reader.pages]
            combined = "\n".join(part.strip() for part in page_text if part.strip()).strip()
            if combined:
                texts.append(combined)
                names.append(uploaded_file.name)
        except Exception:
            continue

    return "\n\n".join(texts).strip(), names


def build_history_chart(history: list[dict[str, Any]]) -> alt.Chart:
    chart_data = pd.DataFrame(
        [
            {"created_at": item["created_at"], "score": item["score"]}
            for item in history[:10]
        ]
    ).iloc[::-1]

    return (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("created_at:N", sort=None, title="Recent analyses"),
            y=alt.Y("score:Q", scale=alt.Scale(domain=[0, 4]), title="Score"),
            color=alt.value("#38bdf8"),
            tooltip=["created_at", "score"],
        )
        .properties(height=250)
    )


def build_model_breakdown_chart(result: dict[str, Any]) -> alt.Chart:
    breakdown = pd.DataFrame(
        [
            {"label": "Positive", "value": result["pos"]},
            {"label": "Neutral", "value": result["neu"]},
            {"label": "Negative", "value": result["neg"]},
        ]
    )

    return (
        alt.Chart(breakdown)
        .mark_bar(cornerRadiusEnd=8)
        .encode(
            x=alt.X("label:N", sort=["Positive", "Neutral", "Negative"], title="Model output"),
            y=alt.Y("value:Q", scale=alt.Scale(domain=[0, 1]), title="Probability"),
            color=alt.Color("label:N", scale=alt.Scale(domain=["Positive", "Neutral", "Negative"], range=["#22c55e", "#eab308", "#ef4444"]), legend=None),
            tooltip=["label", alt.Tooltip("value:Q", format=".2f")],
        )
        .properties(height=250)
    )


def main() -> None:
    ensure_state()

    if "theme_switch" not in st.session_state:
        st.session_state.theme_switch = st.session_state.ui_theme == "light"

    theme = "light" if st.session_state.theme_switch else "dark"
    st.session_state.ui_theme = theme
    inject_styles(theme)

    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown(
            """
            <div class="theme-shell">
                <div>
                    <div class="theme-label">Sentiment Studio</div>
                    <div class="theme-title">Premium sentiment analysis with a black/light theme switch, PDF input, and model insights.</div>
                </div>
                <div class="tool-chip">Theme-ready UI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_right:
        st.toggle("Light theme", key="theme_switch")

    st.markdown(
        """
        <div class="hero">
            <div class="hero-grid">
                <div>
                    <div class="eyebrow">AI sentiment intelligence</div>
                    <h1>Sentiment Studio</h1>
                    <p>
                        Analyze plain text or uploaded PDFs, inspect the VADER model output, and switch between dark and light themes without leaving the page.
                    </p>
                    <div class="hero-cta">
                        <span class="chip">Text + PDF input</span>
                        <span class="chip">Model breakdown charts</span>
                        <span class="chip">History tracking</span>
                        <span class="chip">CSV export</span>
                    </div>
                </div>
                <div class="hero-panel">
                    <div class="hero-stat"><div class="label">Model</div><div class="value">VADER</div><div class="note">Fast local inference</div></div>
                    <div class="hero-stat"><div class="label">Scale</div><div class="value">0-4</div><div class="note">Neutral centered score</div></div>
                    <div class="hero-stat"><div class="label">Input</div><div class="value">PDF</div><div class="note">Extract text from files</div></div>
                    <div class="hero-stat"><div class="label">Theme</div><div class="value">Dual</div><div class="note">Dark and light modes</div></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    st.markdown(
        """
        <div class="card">
            <div class="section-kicker">Why Sentiment Studio?</div>
            <div class="feature-grid">
                <div class="feature-card"><h4>Instant Results</h4><p>Analyze feedback immediately with a lightweight model and see the sentiment score, confidence, and keyword highlights.</p></div>
                <div class="feature-card"><h4>PDF Ready</h4><p>Upload one or more PDFs, extract text, and send the content straight into the model without leaving the page.</p></div>
                <div class="feature-card"><h4>Model Analytics</h4><p>Explore score trend, sentiment breakdown, and keyword focus in a layout designed to stay clean and readable.</p></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    st.markdown(
        """
        <div class="card">
            <div class="section-kicker">Model Pipeline</div>
            <div class="pipeline">
                <div class="step-card"><div class="step-index">1</div><h4>Collect Input</h4><p>Paste text or upload PDFs to build your analysis sample.</p></div>
                <div class="step-card"><div class="step-index">2</div><h4>Extract Text</h4><p>The app reads PDF text and prepares it for the sentiment engine.</p></div>
                <div class="step-card"><div class="step-index">3</div><h4>Analyze Sentiment</h4><p>VADER returns polarity scores, confidence, and the final sentiment label.</p></div>
                <div class="step-card"><div class="step-index">4</div><h4>Visualize</h4><p>See the model output, score trend, and keyword focus in compact charts.</p></div>
                <div class="step-card"><div class="step-index">5</div><h4>Export</h4><p>Download CSV or a report for sharing and quick review.</p></div>
                <div class="step-card"><div class="step-index">6</div><h4>Switch Theme</h4><p>Use the dark or light view depending on your preference and environment.</p></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    left, right = st.columns([1.25, 1])
    result = st.session_state.current_result
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-kicker">Predict</div>', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Text to Analyze</h3>', unsafe_allow_html=True)
        st.markdown('<div class="small-note">Type text, use a sample, or load text from a PDF and analyze it directly.</div>', unsafe_allow_html=True)

        sample_choice = st.selectbox("Quick samples", ["Custom input", *SAMPLE_TEXTS.keys()], label_visibility="collapsed")
        if sample_choice != "Custom input":
            st.session_state.current_text = SAMPLE_TEXTS[sample_choice]

        current_text = st.text_area(
            "Enter text",
            value=st.session_state.current_text,
            height=250,
            max_chars=MAX_CHARS,
            placeholder="Paste feedback, comments, reviews, or messages here...",
            label_visibility="collapsed",
        )
        st.session_state.current_text = current_text

        c1, c2, c3 = st.columns(3)
        with c1:
            analyze_clicked = st.button("Analyze text", use_container_width=True, type="primary")
        with c2:
            clear_clicked = st.button("Clear", use_container_width=True)
        with c3:
            sample_clicked = st.button("Use positive sample", use_container_width=True)

        if sample_clicked:
            st.session_state.current_text = SAMPLE_TEXTS["Positive sample"]
            st.rerun()
        if clear_clicked:
            st.session_state.current_text = ""
            st.session_state.current_result = None
            st.session_state.error = ""
            st.session_state.pdf_text = ""
            st.session_state.pdf_names = []
            st.session_state.last_pdf_signature = ""
            st.rerun()

        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-kicker">PDF input</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            key="pdf_uploader",
            label_visibility="collapsed",
            help="Upload one or more text-based PDFs. Scanned PDFs without embedded text may not extract cleanly.",
        )

        pdf_text = ""
        pdf_names: list[str] = []
        if uploaded_files:
            pdf_text, pdf_names = extract_pdf_text(uploaded_files)
            st.session_state.pdf_text = pdf_text
            st.session_state.pdf_names = pdf_names

            if not pdf_text:
                st.warning("The uploaded PDF appears to contain no extractable text. If this is a scanned document, OCR is needed before sentiment analysis.")
                st.session_state.error = ""

            pdf_signature = f"{'|'.join(pdf_names)}:{len(pdf_text)}"
            if pdf_text and pdf_signature != st.session_state.last_pdf_signature:
                if len(pdf_text) > MAX_CHARS:
                    st.session_state.error = f"The extracted PDF text is too long. Please keep it under {MAX_CHARS} characters."
                else:
                    record = analyze_text(pdf_text)
                    st.session_state.current_result = record
                    st.session_state.current_text = pdf_text
                    st.session_state.error = ""
                    push_history(record)
                    st.session_state.last_pdf_signature = pdf_signature
                    st.success("PDF analyzed successfully.")

        if pdf_names:
            st.markdown(f'<div class="pdf-pill">Loaded {len(pdf_names)} PDF(s) · {len(pdf_text):,} extracted characters</div>', unsafe_allow_html=True)
            st.caption(", ".join(pdf_names[:3]) + (" ..." if len(pdf_names) > 3 else ""))
            pdf_load_col, pdf_analyze_col = st.columns(2)
            with pdf_load_col:
                load_pdf_clicked = st.button("Load PDF text", use_container_width=True)
            with pdf_analyze_col:
                analyze_pdf_clicked = st.button("Analyze PDF", use_container_width=True)
        else:
            load_pdf_clicked = False
            analyze_pdf_clicked = False
            st.caption("PDF text will appear here after upload.")
        st.markdown('</div>', unsafe_allow_html=True)

        if load_pdf_clicked and pdf_text:
            st.session_state.current_text = pdf_text[:MAX_CHARS]
            st.rerun()

        if analyze_pdf_clicked and pdf_text:
            if len(pdf_text) > MAX_CHARS:
                st.session_state.error = f"The extracted PDF text is too long. Please keep it under {MAX_CHARS} characters."
            else:
                record = analyze_text(pdf_text)
                st.session_state.current_result = record
                st.session_state.current_text = pdf_text
                st.session_state.error = ""
                push_history(record)
            st.rerun()

        if analyze_clicked:
            text = current_text.strip()
            if not text:
                st.session_state.error = "Please enter some text to analyze."
            elif len(text) > MAX_CHARS:
                st.session_state.error = f"Text is too long. Please keep it under {MAX_CHARS} characters."
            else:
                record = analyze_text(text)
                st.session_state.current_result = record
                st.session_state.error = ""
                push_history(record)
                result = record

        if st.session_state.error:
            st.error(st.session_state.error)

        if st.session_state.current_result is None and current_text.strip():
            st.info("Run analysis to view the current sentiment summary.")

        if result is not None:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric"><div class="metric-label">Current</div><div class="metric-value {sentiment_badge_class(result['sentiment'])}">{result['sentiment']}</div><div class="metric-note">{result['emoji']}</div></div>
                    <div class="metric"><div class="metric-label">Score</div><div class="metric-value">{result['score']}</div><div class="metric-note">0 to 4 scale</div></div>
                    <div class="metric"><div class="metric-label">Confidence</div><div class="metric-value">{result['confidence_text']}</div><div class="metric-note">Model strength</div></div>
                    <div class="metric"><div class="metric-label">Text Length</div><div class="metric-value">{len(result['text'])}</div><div class="metric-note">characters</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(min(1.0, max(0.0, result["score"] / 4.0)))
        else:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric"><div class="metric-label">Current</div><div class="metric-value result-neutral">Neutral</div><div class="metric-note">😐</div></div>
                    <div class="metric"><div class="metric-label">Score</div><div class="metric-value">2</div><div class="metric-note">0 to 4 scale</div></div>
                    <div class="metric"><div class="metric-label">Confidence</div><div class="metric-value">0%</div><div class="metric-note">Model strength</div></div>
                    <div class="metric"><div class="metric-label">Text Length</div><div class="metric-value">0</div><div class="metric-note">characters</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(0)

        st.markdown("<div class='footer-note'>History stays in the current session. PDF analysis uses extracted text only.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-kicker">Model Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Model Profile</h3>', unsafe_allow_html=True)
        st.write(MODEL_NAME)
        st.write(MODEL_DESCRIPTION)
        st.caption(MODEL_TECH)
        st.markdown('</div>', unsafe_allow_html=True)

        history = st.session_state.history
        st.markdown('<div class="chart-stack">', unsafe_allow_html=True)

        if result is not None:
            st.markdown('<div class="card chart-card">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-title">Model Output Breakdown</h3>', unsafe_allow_html=True)
            st.altair_chart(build_model_breakdown_chart(result), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if history:
            st.markdown('<div class="card chart-card">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-title">Sentiment Score Trend</h3>', unsafe_allow_html=True)
            st.altair_chart(build_history_chart(history), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            terms_df = top_terms(history)
            term_chart = (
                alt.Chart(terms_df)
                .mark_bar(cornerRadiusEnd=6)
                .encode(
                    x=alt.X("count:Q", title="Frequency"),
                    y=alt.Y("word:N", sort="-x", title="Top words"),
                    color=alt.value("#0ea5e9"),
                    tooltip=["word", "count"],
                )
                .properties(height=220)
            )

            st.markdown('<div class="card chart-card">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-title">Keyword Focus</h3>', unsafe_allow_html=True)
            st.altair_chart(term_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card chart-card">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-title">Sentiment Score Trend</h3>', unsafe_allow_html=True)
            st.info("Analyze text or upload a PDF to populate the model graphs.")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="cta-band">', unsafe_allow_html=True)
    st.markdown('<div><div class="section-kicker">Ready to analyze</div><h3 class="section-title">Recent Analyses</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="tech-grid"><span class="tool-chip">PDF upload</span><span class="tool-chip">CSV download</span><span class="tool-chip">Light / Dark</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if history:
        history_df = pd.DataFrame(history)[["created_at", "sentiment", "score", "emoji", "confidence_text", "text"]]
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        csv_data = export_history_csv(history)
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name="sentiment-history.csv",
            mime="text/csv",
            use_container_width=False,
        )
        if result is not None:
            summary = (
                f"Sentiment Studio Report\n\n"
                f"Text: {result['text']}\n"
                f"Sentiment: {result['sentiment']}\n"
                f"Score: {result['score']}\n"
                f"Confidence: {result['confidence_text']}\n"
                f"Generated: {result['created_at']}\n"
            )
            st.download_button(
                "Download report",
                data=summary,
                file_name="sentiment-report.txt",
                mime="text/plain",
                use_container_width=False,
            )
    else:
        st.info("No analyses yet. Run one to build history.")

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
