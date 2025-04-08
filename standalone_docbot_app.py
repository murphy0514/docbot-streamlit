import streamlit as st
import openai
import os
from PyPDF2 import PdfReader

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Helper: Extract text from PDF
def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text[:25000]

# Helper: Query GPT
def query_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        timeout=90
    )
    return response["choices"][0]["message"]["content"]

# App UI
st.title("📄 AI-Powered Document Tool")

mode = st.selectbox("Select Mode", ["Highlight Terms in One Document", "Compare Two Documents"])
query = st.text_input("What are you looking for?", placeholder="e.g. Highlight all payments to XYZ")

file1 = st.file_uploader("Upload Document 1", type="pdf")
file2 = None

if mode == "Compare Two Documents":
    file2 = st.file_uploader("Upload Document 2", type="pdf")

if st.button("Analyze"):
    if not query or not file1:
        st.error("Please provide a query and upload at least one document.")
    elif mode == "Compare Two Documents" and not file2:
        st.error("Please upload the second document for comparison.")
    else:
        try:
            text1 = extract_text(file1)
            if mode == "Highlight Terms in One Document":
                prompt = f"""
You are a document reviewer for a Canadian law firm. A user has uploaded a document and asked to highlight specific items.

Document:
{text1}

Query: {query}

Please list all relevant highlighted segments from the document. Include a snippet of surrounding context and format clearly. Use bullet points or sections.
"""
                result = query_gpt(prompt)
                st.success("Highlights:")
                st.markdown(result)
            else:
                text2 = extract_text(file2)
                prompt = f"""
You are a legal assistant. Compare the following two documents:

--- Document 1 ---
{text1}

--- Document 2 ---
{text2}

Query: {query}

Provide a structured, professional comparison report. Highlight key differences in clauses, wording, and any financial terms. Use bullet points or tables if helpful. Use Canadian dollars only.
"""
                result = query_gpt(prompt)
                st.success("Comparison Report:")
                st.markdown(result)
        except Exception as e:
            st.error(f"Error: {str(e)}")