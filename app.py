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
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(
    page_title="Sentiment Studio",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(168, 85, 247, 0.16), transparent 24%),
            linear-gradient(180deg, #08111f 0%, #0b1220 45%, #09101b 100%);
        color: #e5eefb;
        font-family: "Space Grotesk", "Segoe UI", sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .hero {
        padding: 1.5rem 1.6rem;
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 24px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.84), rgba(15, 23, 42, 0.56));
        box-shadow: 0 20px 60px rgba(2, 6, 23, 0.35);
    }

    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.16em;
        font-size: 0.72rem;
        color: #7dd3fc;
        margin-bottom: 0.45rem;
    }

    .hero h1 {
        font-size: clamp(2.2rem, 4vw, 3.8rem);
        margin: 0;
        line-height: 1;
    }

    .hero p {
        margin: 0.85rem 0 0;
        color: #cbd5e1;
        max-width: 70ch;
        font-size: 1.02rem;
    }

    .chip-row {
        display: flex;
        gap: 0.55rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.42rem 0.75rem;
        border: 1px solid rgba(148, 163, 184, 0.22);
        background: rgba(15, 23, 42, 0.55);
        color: #e2e8f0;
        font-size: 0.82rem;
    }

    .card {
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.62));
        padding: 1.2rem;
        box-shadow: 0 18px 45px rgba(2, 6, 23, 0.22);
    }

    .metric-card {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.8rem;
        margin-top: 1rem;
    }

    .metric {
        border-radius: 18px;
        padding: 1rem;
        background: rgba(2, 6, 23, 0.28);
        border: 1px solid rgba(148, 163, 184, 0.14);
    }

    .metric-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: #94a3b8;
    }

    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        margin-top: 0.25rem;
        color: #f8fafc;
    }

    .metric-note {
        margin-top: 0.3rem;
        color: #cbd5e1;
        font-size: 0.85rem;
    }

    .result-positive { color: #86efac; }
    .result-negative { color: #fda4af; }
    .result-neutral { color: #fcd34d; }

    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.75) !important;
        color: #e5eefb !important;
        border: 1px solid rgba(148, 163, 184, 0.22) !important;
        border-radius: 16px !important;
        min-height: 180px;
    }

    .small-note {
        color: #94a3b8;
        font-size: 0.9rem;
    }

    .section-title {
        margin: 0 0 0.75rem;
        font-size: 1.15rem;
    }

    .footer-note {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 1rem;
    }

    @media (max-width: 900px) {
        .metric-card {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
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


def main() -> None:
    ensure_state()

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">AI sentiment intelligence</div>
            <h1>Sentiment Studio</h1>
            <p>
                Analyze feedback, reviews, or messages in a polished Streamlit interface.
                The app keeps a local history, exposes score and confidence, and is ready for deployment.
            </p>
            <div class="chip-row">
                <span class="chip">Live sentiment</span>
                <span class="chip">CSV export</span>
                <span class="chip">History tracking</span>
                <span class="chip">Streamlit deployable</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Text to Analyze</h3>', unsafe_allow_html=True)

        sample_choice = st.selectbox("Quick samples", ["Custom input", *SAMPLE_TEXTS.keys()], label_visibility="collapsed")
        if sample_choice != "Custom input":
            st.session_state.current_text = SAMPLE_TEXTS[sample_choice]

        current_text = st.text_area(
            "Enter text",
            value=st.session_state.current_text,
            height=220,
            max_chars=MAX_CHARS,
            placeholder="Paste feedback, comments, reviews, or messages here...",
            label_visibility="collapsed",
        )
        st.session_state.current_text = current_text

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            analyze_clicked = st.button("Analyze sentiment", use_container_width=True, type="primary")
        with c2:
            clear_clicked = st.button("Clear", use_container_width=True)
        with c3:
            positive_clicked = st.button("Positive sample", use_container_width=True)
        with c4:
            negative_clicked = st.button("Negative sample", use_container_width=True)

        if positive_clicked:
            st.session_state.current_text = SAMPLE_TEXTS["Positive sample"]
            st.rerun()
        if negative_clicked:
            st.session_state.current_text = SAMPLE_TEXTS["Negative sample"]
            st.rerun()
        if clear_clicked:
            st.session_state.current_text = ""
            st.session_state.current_result = None
            st.session_state.error = ""
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

        if st.session_state.error:
            st.error(st.session_state.error)

        if st.session_state.current_result is None and current_text.strip():
            st.info("Run analysis to view the current sentiment summary.")

        if st.session_state.current_result is not None:
            result = st.session_state.current_result
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric">
                        <div class="metric-label">Current</div>
                        <div class="metric-value {sentiment_badge_class(result['sentiment'])}">{result['sentiment']}</div>
                        <div class="metric-note">{result['emoji']}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Score</div>
                        <div class="metric-value">{result['score']}</div>
                        <div class="metric-note">0 to 4 scale</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Confidence</div>
                        <div class="metric-value">{result['confidence_text']}</div>
                        <div class="metric-note">Model strength</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Text Length</div>
                        <div class="metric-value">{len(result['text'])}</div>
                        <div class="metric-note">characters</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(min(1.0, max(0.0, result["score"] / 4.0)))
        else:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric">
                        <div class="metric-label">Current</div>
                        <div class="metric-value result-neutral">Neutral</div>
                        <div class="metric-note">😐</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Score</div>
                        <div class="metric-value">2</div>
                        <div class="metric-note">0 to 4 scale</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Confidence</div>
                        <div class="metric-value">0%</div>
                        <div class="metric-note">Model strength</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Text Length</div>
                        <div class="metric-value">0</div>
                        <div class="metric-note">characters</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(0)

        st.markdown("<div class='footer-note'>The app stores history only in your browser session.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Model Details</h3>', unsafe_allow_html=True)
        st.write(MODEL_NAME)
        st.write(MODEL_DESCRIPTION)
        st.caption(MODEL_TECH)
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("")

        history = st.session_state.history
        if history:
            chart_data = pd.DataFrame([
                {"created_at": item["created_at"], "score": item["score"]}
                for item in history[:10]
            ])
            chart_data = chart_data.iloc[::-1]
            chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("created_at:N", sort=None, title="Recent analyses"),
                y=alt.Y("score:Q", scale=alt.Scale(domain=[0, 4]), title="Score"),
                color=alt.value("#38bdf8"),
                tooltip=["created_at", "score"],
            ).properties(height=260)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-title">Sentiment Score Chart</h3>', unsafe_allow_html=True)
            st.altair_chart(chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.write("")
            terms_df = top_terms(history)
            term_chart = alt.Chart(terms_df).mark_bar(cornerRadiusEnd=6).encode(
                x=alt.X("count:Q", title="Frequency"),
                y=alt.Y("word:N", sort="-x", title="Top words"),
                color=alt.value("#a78bfa"),
                tooltip=["word", "count"],
            ).properties(height=260)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-title">Keyword Focus</h3>', unsafe_allow_html=True)
            st.altair_chart(term_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-title">Sentiment Score Chart</h3>', unsafe_allow_html=True)
            st.info("Analyze some text to populate the chart and keyword view.")
            st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">Recent Analyses</h3>', unsafe_allow_html=True)

    if history:
        history_df = pd.DataFrame(history)[["created_at", "sentiment", "score", "emoji", "confidence_text", "text"]]
        filtered = st.dataframe(history_df, use_container_width=True, hide_index=True)
        csv_data = export_history_csv(history)
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name="sentiment-history.csv",
            mime="text/csv",
            use_container_width=False,
        )
        if st.session_state.current_result is not None:
            report = st.session_state.current_result
            summary = (
                f"Sentiment Studio Report\n\n"
                f"Text: {report['text']}\n"
                f"Sentiment: {report['sentiment']}\n"
                f"Score: {report['score']}\n"
                f"Confidence: {report['confidence_text']}\n"
                f"Generated: {report['created_at']}\n"
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
