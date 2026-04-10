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


# CLEAN TEXT
def clean_text(value):
    if pd.isna(value):
        return ""
    text = str(value)
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


# CHECKLIST
def generate_checklist_from_prd(prd_text):
    text = prd_text.lower()

    return {
        "Acceptance criteria": any(w in text for w in ["acceptance criteria", "given", "when", "then"]),
        "KPIs / metrics": any(w in text for w in ["kpi", "metric", "conversion rate", "latency"]),
        "Edge cases": any(w in text for w in ["error", "failure", "edge case"]),
        "Dependencies": any(w in text for w in ["dependency", "integration", "third-party"]),
        "Security / privacy": any(w in text for w in ["security", "privacy", "authentication"]),
    }


# FILE READERS
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def read_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])


def read_txt(file):
    return file.read().decode("utf-8")


# STYLE
st.markdown(f"""
<style>
.stApp {{ background-color: {BG_COLOR}; color: {TEXT_COLOR}; }}
.card {{
    background-color: {CARD_COLOR};
    padding: 20px;
    border-radius: 16px;
    border: 1px solid {BORDER_COLOR};
    margin-bottom: 16px;
}}
.metric {{ font-size: 34px; font-weight: 800; }}
</style>
""", unsafe_allow_html=True)


# SESSION
if "analysis_df" not in st.session_state:
    st.session_state.analysis_df = None


# HEADER
st.title("Requirements Gap Analyzer")
st.write("Analyze PRDs for missing or unclear requirements")


# 🔥 INPUT MODE
input_mode = st.radio(
    "Choose input type",
    ["Paste PRD Text", "Upload File"],
    horizontal=True
)

prd_text = ""


# TEXT INPUT
if input_mode == "Paste PRD Text":
    prd_text = st.text_area("Paste your PRD", height=300)


# FILE INPUT
else:
    uploaded_file = st.file_uploader(
        "Upload PRD file",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file:
        file_type = uploaded_file.name.split(".")[-1]

        try:
            if file_type == "pdf":
                prd_text = read_pdf(uploaded_file)

            elif file_type == "docx":
                prd_text = read_docx(uploaded_file)

            elif file_type == "txt":
                prd_text = read_txt(uploaded_file)

            st.success("File uploaded and parsed successfully!")

            # Preview
            with st.expander("Preview extracted text"):
                st.write(prd_text[:2000])

        except Exception as e:
            st.error(f"Error reading file: {e}")


# BUTTON
analyze_clicked = st.button(
    "Analyze PRD",
    disabled=not prd_text.strip()
)


# ANALYSIS
if analyze_clicked:
    with st.spinner("Analyzing PRD..."):
        findings = analyze_prd(prd_text)
        df = pd.DataFrame(findings)

        for col in ["category", "problem", "why_it_matters", "suggestion", "severity"]:
            if col in df.columns:
                df[col] = df[col].apply(clean_text)

        df["severity"] = pd.Categorical(df["severity"], ["High", "Medium", "Low"], ordered=True)
        df = df.sort_values("severity")

        st.session_state.analysis_df = df


# DISPLAY
if st.session_state.analysis_df is not None:

    df = st.session_state.analysis_df

    high = (df["severity"] == "High").sum()
    medium = (df["severity"] == "Medium").sum()
    low = (df["severity"] == "Low").sum()

    score = max(100 - (high*15 + medium*8 + low*3), 0)

    color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"

    st.markdown("## PRD Quality Score")
    st.markdown(f"""
    <div class="card">
        <div class="metric" style="color:{color}">{score}/100</div>
        <div style="color:{MUTED_TEXT}">Higher score = fewer gaps</div>
    </div>
    """, unsafe_allow_html=True)

    # CHECKLIST
    st.markdown("## Requirement Coverage Checklist")
    checklist = generate_checklist_from_prd(prd_text)

    for k, v in checklist.items():
        st.write(f"{'✅' if v else '❌'} {k}")

    # RESULTS
    st.markdown("## Analysis Results")

    for _, row in df.iterrows():
        st.markdown(f"### {row['category']} ({row['severity']})")
        st.write("**Problem:**", row["problem"])
        st.write("**Why:**", row["why_it_matters"])
        st.write("**Fix:**", row["suggestion"])
        st.markdown("---")

    # DOWNLOAD
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Report",
        data=csv,
        file_name="prd_analysis.csv"
    )