import streamlit as st
import google.generativeai as genai
import json

# Setup the page look
st.set_page_config(page_title="RBI Assistant MCQ Portal", layout="wide")
st.title("📖 Daily News to MCQ Generator")
st.info("Goal: 11 Hours Study. Current Focus: RBI Assistant & Insurance Exams.")

# Securely get the API Key from Streamlit Settings
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Please add your GEMINI_API_KEY to the Streamlit Secrets.")
    st.stop()

# Topic selection
topic = st.selectbox("Which topic are you practicing?", ["Banking Awareness", "Economy", "Insurance", "Current Affairs"])

# Input area
news_input = st.text_area("Paste today's news text here (from RBI, PIB, or The Hindu):", height=200)

if st.button("Generate 5 MCQs"):
    if news_input:
        with st.spinner("Setting the paper..."):
            prompt = f"Act as an RBI Assistant examiner. Based on this news, create 5 MCQs for the {topic} section. Use 5 options (A-E). Provide the answer and a brief explanation for each. Format the output as a simple list."
            response = model.generate_content(prompt)
            st.markdown(response.text)
    else:
        st.warning("Please paste some news first!")
