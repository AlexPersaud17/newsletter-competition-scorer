import asyncio
import streamlit as st
from pdf_utils import newsletter_uploader, newsletter_previewer
from scorer_utils import get_scores, view_scores


def page_config():
    st.set_page_config(
        layout="wide",
        page_title="VE Inc - Newsletter Competition Scorer"
    )
    st.title("Newsletter Competition Scorer")
    st.session_state["score"] = False
    st.session_state["uploaded_files"] = []

    with st.sidebar.header("Reset"):
        if st.button("Reset", type="primary"):
            st.session_state["uploaded_files"] = []
            st.session_state["score"] = False
            st.rerun()


async def app():
    page_config()
    newsletter_uploader()

    pdf_preview, score = st.columns(2)

    with pdf_preview:
        pdf_preview.header("Preview Newsletters")
        newsletter_previewer()

    with score:
        score.header("Score")
        if st.session_state["uploaded_files"] != []:
            if score.button("Begin Scoring"):
                st.session_state["score"] = True
        scores = get_scores()

        view_scores(await scores)


if __name__ == "__main__":
    asyncio.run(app())
