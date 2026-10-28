from html import escape
import json
import os
from json import JSONDecodeError
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent / ".env")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
MAX_BATCH_SIZE = 1000


class APIRequestError(Exception):
    pass


def call_api(path, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        f"{API_BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data is not None else {},
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        try:
            details = json.load(error)
            message = details.get("detail", error.reason)
        except (JSONDecodeError, UnicodeDecodeError):
            message = error.reason
        raise APIRequestError(f"Backend returned HTTP {error.code}: {message}") from error
    except (URLError, TimeoutError) as error:
        raise APIRequestError(
            f"Cannot connect to the backend at {API_BASE_URL}. Start it with `python main.py`."
        ) from error


st.set_page_config(
    page_title="Signal — Sentiment & Intent",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #0b0d14;
        --panel: rgba(20, 23, 35, 0.88);
        --line: rgba(255, 255, 255, 0.085);
        --muted: #9298ad;
        --text: #f5f6fc;
        --violet: #a78bfa;
        --mint: #75e1c2;
    }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 15% 0%, rgba(110, 76, 210, .16), transparent 35%),
            radial-gradient(ellipse at 95% 20%, rgba(47, 190, 160, .08), transparent 28%),
            var(--bg);
        color: var(--text);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: rgba(13, 15, 24, .96);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.4rem; }
    .block-container { max-width: 1280px; padding-top: 2.2rem; padding-bottom: 4rem; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: -.035em; }
    h1 { font-size: clamp(2.2rem, 4vw, 3.45rem) !important; line-height: 1.08 !important; }
    h2 { font-size: 1.5rem !important; }
    p, label, .stCaption { color: #b4b8c8; }
    .brand {
        display: flex; align-items: center; gap: .7rem; margin: 0 0 2rem;
        color: #f6f4ff; font: 800 1.05rem 'Manrope', sans-serif; letter-spacing: -.04em;
    }
    .brand-mark {
        display: grid; place-items: center; width: 34px; height: 34px; border-radius: 11px;
        color: #120f1d; font-size: 1.1rem;
        background: linear-gradient(145deg, #c4b5fd, #83e8cd);
        box-shadow: 0 5px 20px rgba(167, 139, 250, .23);
    }
    .eyebrow {
        color: #b8a5ff; text-transform: uppercase; letter-spacing: .17em;
        font-size: .72rem; font-weight: 700; margin-bottom: .65rem;
    }
    .hero-sub { color: var(--muted); font-size: 1.02rem; max-width: 640px; line-height: 1.7; }
    .status-pill {
        display: inline-flex; align-items: center; gap: .5rem; border: 1px solid rgba(117, 225, 194, .22);
        border-radius: 99px; padding: .5rem .8rem; color: #a3ecd8; font-size: .78rem;
        background: rgba(117, 225, 194, .07); white-space: nowrap;
    }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #75e1c2; box-shadow: 0 0 12px #75e1c2; }
    .surface {
        background: linear-gradient(145deg, rgba(24, 27, 41, .96), rgba(17, 19, 30, .94));
        border: 1px solid var(--line); border-radius: 20px; padding: 1.35rem 1.45rem;
        box-shadow: 0 18px 55px rgba(0, 0, 0, .16);
    }
    .result-card {
        border: 1px solid rgba(167, 139, 250, .26); border-radius: 18px;
        background: linear-gradient(125deg, rgba(110, 76, 210, .16), rgba(117, 225, 194, .055));
        padding: 1.35rem 1.5rem; margin: .8rem 0 1.2rem;
    }
    .result-label { color: var(--muted); font-size: .78rem; text-transform: uppercase; letter-spacing: .13em; }
    .result-value { color: #f5f2ff; font: 800 1.75rem 'Manrope', sans-serif; margin-top: .35rem; }
    .result-kind {
        display: inline-block; margin-top: .65rem; padding: .27rem .65rem; border-radius: 99px;
        color: #c4b5fd; background: rgba(167, 139, 250, .12); font-size: .75rem; font-weight: 700;
    }
    .result-kind.sentiment { color: #90e7d0; background: rgba(117, 225, 194, .1); }
    .section-label { color: #e7e8f1; font: 700 .93rem 'Manrope', sans-serif; margin: .2rem 0 .8rem; }
    .side-note { color: var(--muted); font-size: .82rem; line-height: 1.65; }
    .kicker { color: var(--muted); font-size: .8rem; }
    [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
        border-radius: 14px; border: 1px solid rgba(255,255,255,.12);
        background: rgba(9, 11, 18, .72); color: #f5f6fc;
    }
    [data-testid="stTextArea"] textarea:focus { border-color: rgba(167,139,250,.65); box-shadow: 0 0 0 1px rgba(167,139,250,.3); }
    [data-testid="stBaseButton-primary"] {
        border: 0; color: #14111d; font-weight: 800; border-radius: 12px;
        background: linear-gradient(110deg, #c4b5fd, #83e8cd);
        box-shadow: 0 7px 22px rgba(132, 218, 198, .12);
    }
    [data-testid="stBaseButton-primary"]:hover { color: #14111d; filter: brightness(1.07); }
    [data-testid="stBaseButton-secondary"] {
        border: 1px solid var(--line); color: #d7d8e4; background: rgba(255,255,255,.035);
        border-radius: 11px;
    }
    [data-testid="stMetric"] {
        background: rgba(255,255,255,.035); border: 1px solid var(--line);
        border-radius: 14px; padding: .9rem 1rem;
    }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: #f5f6fc; }
    [data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg, #a78bfa, #75e1c2); }
    [data-testid="stTabs"] button { color: #9da2b5; }
    [data-testid="stTabs"] button[aria-selected="true"] { color: #c4b5fd; }
    hr { border-color: var(--line); }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">✦</span> SIGNAL<span style="color:#9298ad;font-weight:500"> / NLP</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="eyebrow">Workspace</div>', unsafe_allow_html=True)
    st.markdown("### Sentiment & intent")
    st.markdown(
        '<p class="side-note">Understand the feeling behind a message and what the customer wants to do next.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown('<div class="eyebrow">Model snapshot</div>', unsafe_allow_html=True)
    st.markdown("**XGBoost classifier**")
    st.markdown('<p class="side-note">TF-IDF text features · 8 trained classes</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        '<p class="side-note">Built for the <a href="https://www.kaggle.com/datasets/ahsanneural/synthetic-sentiment-and-intent-data" target="_blank" style="color:#c4b5fd">Synthetic Sentiment & Intent dataset</a>.</p>',
        unsafe_allow_html=True,
    )
    st.caption("Local inference · Your text stays in this app")

try:
    model_info = call_api("/model-info")
except APIRequestError as error:
    st.error(str(error))
    st.stop()

header_left, header_right = st.columns([5, 1.25], vertical_alignment="center")
with header_left:
    st.markdown('<div class="eyebrow">Customer intelligence · 01</div>', unsafe_allow_html=True)
    st.title("Know what your customers mean.")
    st.markdown(
        '<p class="hero-sub">Go beyond the words. Detect sentiment and uncover the intent in every customer message.</p>',
        unsafe_allow_html=True,
    )
with header_right:
    st.markdown(
        '<div class="status-pill"><span class="status-dot"></span> API CONNECTED</div>',
        unsafe_allow_html=True,
    )

st.write("")
analyze_tab, batch_tab, about_tab = st.tabs(["✦  Analyze text", "▤  Batch analysis", "ⓘ  About the model"])

with analyze_tab:
    st.markdown('<div class="section-label">Try a message</div>', unsafe_allow_html=True)
    st.markdown('<p class="kicker">Choose an example or write your own. The model supports up to 1,000 characters.</p>', unsafe_allow_html=True)

    example_columns = st.columns(3)
    examples = [
        ("Positive", "The support team was wonderful and solved my issue right away."),
        ("Refund request", "I would like to request a refund for my recent purchase."),
        ("Cancel order", "Please cancel my order before it ships."),
    ]
    for column, (label, sample) in zip(example_columns, examples):
        with column:
            if st.button(label, key=f"example_{label}", use_container_width=True):
                st.session_state["review_text"] = sample

    with st.form("single_prediction"):
        review_text = st.text_area(
            "Customer message",
            key="review_text",
            height=170,
            max_chars=1000,
            placeholder="Paste a customer message here…",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Analyze message  →", type="primary", use_container_width=True)

    if submitted:
        if not review_text.strip():
            st.session_state.pop("prediction_result", None)
            st.warning("Enter a message before running the analysis.")
        else:
            try:
                prediction = call_api(
                    "/predict",
                    {"text": review_text.strip()},
                )
                st.session_state["prediction_result"] = {
                    "label": prediction["label"],
                    "confidence": prediction["confidence"],
                    "probabilities": [
                        (item["label"], item["probability"])
                        for item in prediction["probabilities"]
                    ],
                }
            except APIRequestError as error:
                st.error(str(error))

    result = st.session_state.get("prediction_result")
    if result:
        label = result["label"]
        is_intent = label.startswith("Intent:")
        kind = "Intent" if is_intent else "Sentiment"
        display_label = label.removeprefix("Intent:").strip() if is_intent else label
        kind_class = "" if is_intent else " sentiment"

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">Predicted {kind.lower()}</div>
                <div class="result-value">{escape(display_label)}</div>
                <span class="result-kind{kind_class}">{kind}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        confidence_column, detail_column = st.columns([1, 2])
        with confidence_column:
            st.metric("Model confidence", f"{result['confidence']:.1%}")
        with detail_column:
            st.markdown('<div class="section-label">Class probabilities</div>', unsafe_allow_html=True)
            for class_name, probability in result["probabilities"]:
                label_column, bar_column, value_column = st.columns([1.35, 2, 0.45], vertical_alignment="center")
                label_column.write(class_name)
                bar_column.progress(min(max(probability, 0.0), 1.0))
                value_column.caption(f"{probability:.0%}")

with batch_tab:
    st.markdown('<div class="section-label">Analyze a full dataset</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="kicker">Upload a CSV with a <code>Text</code> column. If it also has <code>Label</code>, '
        'the results will include a comparison with the supplied labels.</p>',
        unsafe_allow_html=True,
    )
    with st.form("batch_prediction"):
        batch_file = st.file_uploader("Choose a CSV file", type=["csv"], key="batch_csv")
        batch_submitted = st.form_submit_button("Run batch analysis  →", type="primary")

    if batch_submitted:
        if batch_file is None:
            st.warning("Choose a CSV file to analyze.")
            st.session_state.pop("batch_result", None)
        else:
            source = pd.read_csv(batch_file)
            if "Text" not in source.columns:
                st.error("This CSV needs a column named `Text`.")
                st.session_state.pop("batch_result", None)
            elif source.empty:
                st.warning("The CSV has no rows to analyze.")
                st.session_state.pop("batch_result", None)
            elif source["Text"].isna().any() or source["Text"].astype(str).str.strip().eq("").any():
                st.error("Every row in the `Text` column must contain a message.")
                st.session_state.pop("batch_result", None)
            elif len(source) > MAX_BATCH_SIZE:
                st.error(f"The backend accepts up to {MAX_BATCH_SIZE:,} messages per batch.")
                st.session_state.pop("batch_result", None)
            else:
                try:
                    response = call_api(
                        "/predict/batch",
                        {"texts": source["Text"].astype(str).tolist()},
                    )
                    predictions = response["predictions"]
                    output = pd.DataFrame(
                        {
                            "Text": source["Text"],
                            "Predicted Label": [item["label"] for item in predictions],
                            "Confidence": [item["confidence"] for item in predictions],
                        }
                    )
                    if "Label" in source.columns:
                        output.insert(1, "Actual Label", source["Label"])
                        output["Correct"] = output["Predicted Label"].eq(source["Label"])
                    st.session_state["batch_result"] = output
                except APIRequestError as error:
                    st.session_state.pop("batch_result", None)
                    st.error(str(error))

    batch_result = st.session_state.get("batch_result")
    if batch_result is not None:
        metric_columns = st.columns(3)
        metric_columns[0].metric("Messages analyzed", f"{len(batch_result):,}")
        metric_columns[1].metric("Average confidence", f"{batch_result['Confidence'].mean():.1%}")
        if "Correct" in batch_result.columns:
            metric_columns[2].metric("Label agreement", f"{batch_result['Correct'].mean():.1%}")
        else:
            metric_columns[2].metric("Label comparison", "Not provided")
        st.dataframe(batch_result, use_container_width=True, hide_index=True)
        st.download_button(
            "Download predictions as CSV",
            data=batch_result.to_csv(index=False).encode("utf-8"),
            file_name="signal_predictions.csv",
            mime="text/csv",
            type="primary",
        )

with about_tab:
    st.markdown('<div class="section-label">A compact view of the pipeline</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="surface">
            <p class="side-note">Messages are transformed with the saved TF-IDF vectorizer and classified by the
            trained XGBoost model. The label encoder maps model output to one of five intents or three sentiment
            classes. Confidence is the model's predicted class probability, not a guarantee of correctness.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    summary_columns = st.columns(3)
    summary_columns[0].metric("Classifier", "XGBoost")
    summary_columns[1].metric("Input features", f"{model_info['feature_count']:,} TF-IDF terms")
    summary_columns[2].metric("Output classes", f"{len(model_info['classes'])}")
    st.markdown("**Available labels**")
    st.write(", ".join(model_info["classes"]))
    st.caption(
        "Predictions are served by the FastAPI backend using the model files in the project folder."
    )
