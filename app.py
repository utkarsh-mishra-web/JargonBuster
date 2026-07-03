# Jargon Buster - A simple Streamlit app that explains legal/medical text in plain language.
# Run with: streamlit run app.py
#
# CHANGED: This app now uses Groq (free tier, no credit card) instead of Google Gemini.
# Groq provides fast access to open-source models like Llama 3 via a simple chat API.

import os

from groq import Groq
import streamlit as st

# ---------------------------------------------------------------------------
# Page setup: title, icon, and layout shown in the browser tab and header.
# (Unchanged from the Gemini version.)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Jargon Buster",
    page_icon="📄",
    layout="centered",
)

# Main heading and short description for users.
st.title("Jargon Buster")
st.markdown(
    "Paste confusing legal or medical text below and get a simple explanation "
    "plus your next action step."
)

# ---------------------------------------------------------------------------
# API key: read from environment variable, or let the user enter it in the sidebar.
# CHANGED: Uses GROQ_API_KEY instead of GOOGLE_API_KEY.
# Get a free key at https://console.groq.com/keys (no credit card required).
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

# ---------------------------------------------------------------------------
# User input: large text box for the document they want explained.
# (Unchanged from the Gemini version.)
# ---------------------------------------------------------------------------
document_text = st.text_area(
    "Paste your document here",
    height=250,
    placeholder="Paste legal letters, medical forms, insurance docs, etc.",
)

# Button to trigger the explanation (only runs when clicked).
submit_clicked = st.button("Explain it simply", type="primary")

# ---------------------------------------------------------------------------
# When the user clicks submit, send the text to Groq and show the result.
# CHANGED: Groq uses a "chat completions" API (messages with roles) instead of
# Gemini's single generate_content() call. We send one user message with the prompt.
# ---------------------------------------------------------------------------
if submit_clicked:
    # Validate inputs before calling the API.
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar.")
    elif not document_text.strip():
        st.warning("Please paste some text to explain.")
    else:
        # CHANGED: Create a Groq client (replaces genai.configure() + GenerativeModel).
        client = Groq(api_key=api_key)

        # The exact prompt you requested, with the user's document appended.
        prompt = (
            "Explain this document to me like I am 5 years old and tell me "
            "what my exact next action step should be.\n\n"
            f"Document:\n{document_text}"
        )

        # Show a spinner while waiting for the API response.
        with st.spinner("Reading your document and simplifying it..."):
            try:
                # Call Groq's chat API with llama-3.1-8b-instant (replaces decommissioned llama3-8b-8192).
                # response.choices[0].message.content holds the AI's reply text.
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
