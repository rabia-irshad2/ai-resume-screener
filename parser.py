import pdfplumber
import re


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract plain text from an uploaded PDF file."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def clean_text(text: str) -> str:
    """Basic text cleaning — lowercase, remove extra whitespace."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def extract_text_from_input(uploaded_file=None, pasted_text: str = "") -> str:
    """
    Return text from either a PDF upload or a pasted text area.
    PDF takes priority if both are provided.
    """
    if uploaded_file is not None:
        return extract_text_from_pdf(uploaded_file)
    return pasted_text.strip()