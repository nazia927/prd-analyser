import re
import html
import pandas as pd
import streamlit as st
from analyzer import analyze_prd
from PyPDF2 import PdfReader
from docx import Document

st.set_page_config(page_title="Requirements Gap Analyzer", layout="wide")

# COLORS
BG_COLOR = "#0b1020"
CARD_COLOR = "#121a2b"
TEXT_COLOR = "#f8fafc"
MUTED_TEXT = "#94a3b8"
ACCENT_COLOR = "#22c55e"
INPUT_BG = "#0f172a"
BORDER_COLOR = "#334155"


def clean_text(value):
    if pd.isna(value):
        return ""
    text = str(value)
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def generate_checklist_from_prd(prd_text):
    text = prd_text.lower()

    return {
        "Acceptance criteria": any(w in text for w in ["acceptance criteria", "given", "when", "then"]),
        "KPIs / metrics": any(w in text for w in ["kpi", "metric", "conversion rate", "latency"]),
        "Edge cases": any(w in text for w in ["error", "failure", "edge case", "exception"]),
        "Dependencies": any(w in text for w in ["dependency", "integration", "third-party"]),
        "Security / privacy": any(w in text for w in ["security", "privacy", "authentication", "authorization"]),
    }


def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text


def read_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])


def read_txt(file):
    return file.read().decode("utf-8")


st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG_COLOR};
        color: {TEXT_COLOR};
    }}

    html, body, [class*="css"] {{
        color: {TEXT_COLOR};
    }}

    .main-title {{
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 8px;
    }}

    .sub-text {{
        font-size: 20px;
        color: {MUTED_TEXT};
        margin-bottom: 24px;
    }}

    .card {{
        background-color: {CARD_COLOR};
        padding: 20px;
        border-radius: 16px;
        border: 1px solid {BORDER_COLOR};
        margin-bottom: 16px;
    }}

    .metric {{
        font-size: 34px;
        font-weight: 800;
    }}

    div[data-baseweb="textarea"] textarea {{
        background-color: {INPUT_BG} !important;
        color: {TEXT_COLOR} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
    }}

    .stButton button {{
        background-color: {CARD_COLOR};
        color: {TEXT_COLOR};
        border: 1px solid {BORDER_COLOR};
        border-radius: 10px;
    }}

    .stButton button:hover {{
        border: 1px solid {ACCENT_COLOR};
        color: {ACCENT_COLOR};
    }}

    .stDownloadButton button {{
        background-color: {ACCENT_COLOR};
        color: #04130a;
        border: none;
        border-radius: 10px;
        font-weight: 700;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

if "analysis_df" not in st.session_state:
    st.session_state.analysis_df = None

if "selected_severity" not in st.session_state:
    st.session_state.selected_severity = ["High", "Medium", "Low"]

if "current_prd_text" not in st.session_state:
    st.session_state.current_prd_text = ""

if "no_issues_detected" not in st.session_state:
    st.session_state.no_issues_detected = False

st.markdown('<div class="main-title">Requirements Gap Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">Analyze PRDs for missing or unclear requirements</div>',
    unsafe_allow_html=True
)

input_mode = st.radio(
    "Choose input type",
    ["Paste PRD Text", "Upload File"],
    horizontal=True
)

prd_text = ""

if input_mode == "Paste PRD Text":
    prd_text = st.text_area("Paste your PRD", height=300)
else:
    uploaded_file = st.file_uploader("Upload PRD file", type=["pdf", "docx", "txt"])

    if uploaded_file:
        file_type = uploaded_file.name.split(".")[-1].lower()

        try:
            if file_type == "pdf":
                prd_text = read_pdf(uploaded_file)
            elif file_type == "docx":
                prd_text = read_docx(uploaded_file)
            elif file_type == "txt":
                prd_text = read_txt(uploaded_file)

            st.success("File uploaded and parsed successfully!")

            with st.expander("Preview extracted text"):
                st.write(prd_text[:3000] if prd_text else "No text could be extracted from this file.")

        except Exception as e:
            st.error(f"Error reading file: {e}")

analyze_clicked = st.button(
    "Analyze PRD",
    disabled=not prd_text.strip()
)

if analyze_clicked:
    with st.spinner("Analyzing PRD..."):
        findings = analyze_prd(prd_text)
        df = pd.DataFrame(findings)

        # FIX: handle perfect / no-issue PRDs safely
        if df.empty:
            st.session_state.no_issues_detected = True
            df = pd.DataFrame(columns=[
                "category", "problem", "why_it_matters", "suggestion", "severity"
            ])
        else:
            st.session_state.no_issues_detected = False

        for col in ["category", "problem", "why_it_matters", "suggestion", "severity"]:
            if col in df.columns:
                df[col] = df[col].apply(clean_text)

        if "severity" in df.columns:
            df["severity"] = pd.Categorical(
                df["severity"],
                ["High", "Medium", "Low"],
                ordered=True
            )
            df = df.sort_values("severity")

        st.session_state.analysis_df = df
        st.session_state.current_prd_text = prd_text

if st.session_state.analysis_df is not None:
    df = st.session_state.analysis_df.copy()
    prd_text_for_checklist = st.session_state.current_prd_text

    if st.session_state.no_issues_detected:
        st.success("High-quality PRD detected — minimal gaps found.")

    high = int((df["severity"] == "High").sum()) if "severity" in df.columns else 0
    medium = int((df["severity"] == "Medium").sum()) if "severity" in df.columns else 0
    low = int((df["severity"] == "Low").sum()) if "severity" in df.columns else 0

    score = max(100 - (high * 15 + medium * 8 + low * 3), 0)

    if st.session_state.no_issues_detected:
        score = 100

    if score >= 70:
        color = "#22c55e"
        verdict = "Strong PRD"
    elif score >= 40:
        color = "#f59e0b"
        verdict = "Moderate PRD"
    else:
        color = "#ef4444"
        verdict = "Weak PRD"

    st.markdown("## PRD Quality Score")
    st.markdown(
        f"""
        <div class="card">
            <div class="metric" style="color:{color}">{score}/100</div>
            <div style="color:{MUTED_TEXT}">Higher score = fewer gaps</div>
            <div style="margin-top:10px;font-weight:600">{verdict}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## Requirement Coverage Checklist")
    st.caption("Checklist is based on explicit mentions in the PRD.")

    checklist = generate_checklist_from_prd(prd_text_for_checklist)

    for k, v in checklist.items():
        st.markdown(f"{'✅' if v else '❌'} {k} {'covered' if v else 'missing'}")

    st.markdown("## Summary")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"<div class='card'><div class='metric' style='color:#ef4444'>{high}</div>High</div>",
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"<div class='card'><div class='metric' style='color:#f59e0b'>{medium}</div>Medium</div>",
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"<div class='card'><div class='metric' style='color:#22c55e'>{low}</div>Low</div>",
            unsafe_allow_html=True
        )

    st.markdown("## Filter Results")

    selected = st.multiselect(
        "Severity",
        ["High", "Medium", "Low"],
        default=st.session_state.selected_severity,
        key="selected_severity"
    )

    filtered = df[df["severity"].isin(selected)] if "severity" in df.columns else df

    st.markdown("## Analysis Results")

    if st.session_state.no_issues_detected or filtered.empty:
        st.info("No issues detected for the selected severity levels.")
    else:
        for _, row in filtered.iterrows():
            st.markdown(f"### {row['category']} ({row['severity']})")
            st.write("**Problem:**", row["problem"])
            st.write("**Why it matters:**", row["why_it_matters"])
            st.write("**Suggestion:**", row["suggestion"])
            st.markdown("---")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Report",
        data=csv,
        file_name="prd_analysis.csv"
    )
