# Jargon Buster - A simple Streamlit app that explains legal/medical text in plain language.
# Run with: streamlit run app.py
#
# Uses Groq (free tier, no credit card) for fast access to open-source models like Llama 3.
# Users can paste text OR upload a .txt / .pdf document.

import io
import os

from groq import Groq
import streamlit as st
from PyPDF2 import PdfReader

# ---------------------------------------------------------------------------
# Page setup: title, icon, and layout shown in the browser tab and header.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Jargon Buster",
    page_icon="📄",
    layout="centered",
)

# Main heading and short description for users.
st.title("Jargon Buster")
st.markdown(
    "Paste confusing legal or medical text below, or upload a document, "
    "and get a simple explanation plus your next action step."
)

# ---------------------------------------------------------------------------
# API key: read from environment variable, or let the user enter it in the sidebar.
# Uses GROQ_API_KEY. Get a free key at https://console.groq.com/keys (no credit card required).
# ---------------------------------------------------------------------------
api_key = os.environ.get("GROQ_API_KEY")

with st.sidebar:
    st.header("Settings")
    if not api_key:
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Paste your Groq API key here, or set GROQ_API_KEY in your environment.",
        )
    else:
        st.success("API key loaded from environment.")


def extract_text_from_upload(uploaded_file) -> str:
    """Read plain text from a .txt file or extract text from every page of a .pdf."""
    file_bytes = uploaded_file.read()

    if uploaded_file.name.lower().endswith(".txt"):
        # .txt files are already plain text — decode bytes to a string.
        return file_bytes.decode("utf-8")

    if uploaded_file.name.lower().endswith(".pdf"):
        # PyPDF2 reads the PDF from memory and pulls text from each page.
        reader = PdfReader(io.BytesIO(file_bytes))
        page_texts = []
        for page in reader.pages:
            page_texts.append(page.extract_text() or "")
        return "\n".join(page_texts)

    return ""


# ---------------------------------------------------------------------------
# User input: paste text OR upload a .txt / .pdf file.
# ---------------------------------------------------------------------------
document_text = st.text_area(
    "Paste your document here",
    height=250,
    placeholder="Paste legal letters, medical forms, insurance docs, etc.",
)

uploaded_file = st.file_uploader(
    "Or upload a document",
    type=["txt", "pdf"],
    help="Upload a .txt or .pdf file instead of pasting text.",
)

# Button to trigger the explanation (only runs when clicked).
submit_clicked = st.button("Explain it simply", type="primary")

# ---------------------------------------------------------------------------
# When the user clicks submit, gather text (from upload or text area) and send to Groq.
# ---------------------------------------------------------------------------
if submit_clicked:
    # Validate inputs before calling the API.
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar.")
    else:
        # Prefer uploaded file content; fall back to the text area if no file was uploaded.
        if uploaded_file is not None:
            try:
                document_text = extract_text_from_upload(uploaded_file)
            except Exception as e:
                st.error(f"Could not read the uploaded file: {e}")
                document_text = ""
        # else: document_text already holds whatever the user pasted

        if not document_text.strip():
            st.warning("Please paste some text or upload a .txt / .pdf file to explain.")
        else:
            client = Groq(api_key=api_key)

            # The exact prompt, with the document text appended.
            prompt = (
                "Explain this document to me like I am 5 years old and tell me "
                "what my exact next action step should be.\n\n"
                f"Document:\n{document_text}"
            )

            with st.spinner("Reading your document and simplifying it..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "user", "content": prompt},
                        ],
                    )
                    explanation = response.choices[0].message.content

                    st.subheader("Your simple explanation")
                    st.markdown(explanation)

                except Exception as e:
                    st.error(f"Something went wrong: {e}")
                    st.info(
                        "Check that your Groq API key is valid and that you have internet access."
                    )
