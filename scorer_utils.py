import streamlit as st
import asyncio
import pandas as pd
from xml_utils import format_response, extract_xml
from model_utils import call_model


def view_scores(scores):
    rows = []
    for score in scores:
        root = format_response(score)
        if root is not None:
            row = extract_xml(root)
            if row:
                rows.append(row)
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(data=df,
                     hide_index=True)


async def score_all():
    tasks = [call_model(file) for file in st.session_state["uploaded_files"]]
    return await asyncio.gather(*tasks)


async def get_scores():
    if not st.session_state["uploaded_files"]:
        st.info("Please \"upload\" newsletters first.")
        return []

    if not st.session_state.get("score"):
        return []

    scores = await score_all()
    return scores
