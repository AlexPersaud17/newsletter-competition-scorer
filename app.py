from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig
import os
from dotenv import load_dotenv
from prompt import SYSTEM_PROMPT, USER_PROMPT
import pandas as pd
from xml.etree import ElementTree as ET
import html
import asyncio
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

load_dotenv()

CLIENT = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash-preview-04-17"


def page_config():
    st.set_page_config(layout="wide")
    st.title("Newsletter Competition Judge")
    st.session_state["score"] = False
    st.session_state["uploaded_files"] = []
    with st.sidebar.header("Reset"):
        if st.button("Reset", type="primary"):
            st.session_state["uploaded_files"] = []
            st.session_state["score"] = False
            st.rerun()


async def call_model_async(file):
    pdf_bytes = types.Part.from_bytes(
        data=file.getvalue(), mime_type='application/pdf'
    )
    with st.spinner(f"Scoring {file.name}..."):
        try:
            response = await CLIENT.aio.models.generate_content(
                model=MODEL,
                contents=[pdf_bytes, USER_PROMPT],
                config=GenerateContentConfig(
                    system_instruction=[SYSTEM_PROMPT])
            )
            return response.text
        except Exception as e:
            return f"<company><name>{file.name}</name><comment>Model call failed: {e}</comment></company>"


def newsletter_uploader():
    st.sidebar.header("Upload Newsletters")
    with st.sidebar.header("Upload"):
        with st.form("uploader-form", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "Choose a file",
                accept_multiple_files=True,
                type=["pdf"])
            st.form_submit_button("Upload")

    if uploaded_files:
        st.session_state["uploaded_files"] = uploaded_files
    return st.session_state["uploaded_files"]


def newsletter_previewer():
    uploaded_files = st.session_state.get("uploaded_files", [])
    if uploaded_files is not None:
        with st.spinner("Uploading..."):
            for file in uploaded_files:
                with st.expander(file.name):
                    with st.container(height=500):
                        pdf_viewer(file.getvalue(), pages_vertical_spacing=10)


def format_response(response):
    try:
        escaped_data = response.replace("&", "&amp;")
        wrapped_data = f"<root>{escaped_data}</root>"
        root = ET.fromstring(wrapped_data)
        return root
    except ET.ParseError as e:
        st.error(f"XML Parsing failed: {e}")
        return None


def create_table_row(root):
    for company in root.findall('company'):
        row = {
            'Name': html.unescape(company.findtext('name')),
            'Employee Announcements and Recognition': company.findtext('recog_score'),
            'Company Events': company.findtext('events_score'),
            'Company and Mission': company.findtext('mission_score'),
            'Presentation': company.findtext('pres_score'),
            'Industry Trends and Market News': company.findtext('trends_score'),
            'Comment': company.findtext('comment').strip()
        }
        return row


def create_table(scores):
    rows = []
    for score in scores:
        root = format_response(score)
        if root is not None:
            row = create_table_row(root)
            if row:
                rows.append(row)
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(data=df, width=800)


async def score_all(files):
    tasks = [call_model_async(file) for file in files]
    return await asyncio.gather(*tasks)


async def start_scoring():
    uploaded_files = st.session_state.get("uploaded_files", [])
    if not uploaded_files:
        st.info("Please \"upload\" newsletters first.")
        return []

    if not st.session_state.get("score"):
        return []

    scores = await score_all(uploaded_files)
    return scores


async def app():
    page_config()
    pdf_preview, score = st.columns(2)

    with pdf_preview:
        pdf_preview.header("Newsletter Preview")
        newsletter_uploader()
        newsletter_previewer()

    with score:
        score.header("Score")
        if score.button("Begin Scoring"):
            st.session_state["score"] = True
        scores = start_scoring()

        create_table(await scores)


if __name__ == "__main__":
    asyncio.run(app())
