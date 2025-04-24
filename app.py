import streamlit as st
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_bytes
import json
import requests
import os

# Hugging Face API Configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"  # Public model



# Function to extract text from both text-based and image-based PDFs

def extract_text_from_pdf(pdf_file):
    text = ""

    # Attempt to read with PyPDF2 (text-based PDFs)
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    # If no text found, fallback to OCR
    if not text.strip():
        pdf_file.seek(0)  # Reset pointer to beginning of file
        images = convert_from_bytes(pdf_file.read())
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"

    print(text)
    return text.strip()




# Function to extract key fields using a publicly available model API
def extract_fields(text):
    api_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}  # Replace with your API key

    prompt = f"""
    Extract the following fields from the given invoice text:
    - Invoice Number
    - Invoice Date
    - Supplier Name
    - Supplier Address
    - Buyer/Client Name
    - Buyer/Client Address
    - Total Amount
    - Tax Amount
    - Currency
    - Payment Terms
    - Line Items (Description, Quantity, Unit Price, Total Price)

    Invoice Text:
    {text}

    Provide the output in JSON format.
    """

    payload = {
        "inputs": prompt,
        "parameters": {
            "return_full_text": False,
            "max_new_tokens": 512
        }
    }
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            print("here")
            print(response.json()[0])
            print(response.json()[0]["generated_text"])
            return json.loads(response.json()[0]["generated_text"])
        except Exception as e:
            return {"error": f"Failed to parse JSON: {e}"}
    else:
        return {"error": f"Failed API call: {response.status_code}, {response.text}"}

# Streamlit UI
st.title("Invoice Data Extraction POC")

uploaded_file = st.file_uploader("Upload an Invoice PDF", type=["pdf"])
if uploaded_file:
    with st.spinner("Extracting text..."):
        extracted_text = extract_text_from_pdf(uploaded_file)

    st.text_area("Extracted Text", extracted_text, height=300)

    with st.spinner("Extracting key fields..."):
        extracted_data = extract_fields(extracted_text)

    st.subheader("Extracted Data")
    st.json(extracted_data)
