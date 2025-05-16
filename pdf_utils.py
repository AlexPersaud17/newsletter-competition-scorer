import streamlit as st
from streamlit_pdf_viewer import pdf_viewer


def newsletter_uploader():
    st.sidebar.header("Upload Newsletters")
    with st.sidebar.form("uploader-form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            label="Browse for newsletters",
            help="Upload newsletters in PDF format",
            accept_multiple_files=True,
            type=["pdf"]
        )
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
