import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig, Part
from prompt import SYSTEM_PROMPT, USER_PROMPT

load_dotenv()

CLIENT = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash-preview-04-17"


async def call_model(file):
    with st.spinner(f"Scoring {file.name}..."):
        pdf_bytes = Part.from_bytes(
            data=file.getvalue(), mime_type='application/pdf'
        )
        try:
            response = await CLIENT.aio.models.generate_content(
                model=MODEL,
                contents=[pdf_bytes, USER_PROMPT],
                config=GenerateContentConfig(
                    system_instruction=[SYSTEM_PROMPT])
            )
            return response.text
        except Exception as e:
            st.error(f"Model call failed: {e}")
            return f"<company><name>{file.name}</name><comment>Model call failed: {e}</comment></company>"
