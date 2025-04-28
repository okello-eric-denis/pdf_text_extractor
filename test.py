import re

import fitz  # PyMuPDF
import streamlit as st
from PIL import Image, ImageDraw

# Define the fields and their regex patterns
FIELDS = {
    "Applicant Name": r"Applicant Name\s*([A-Z\s]+)",
    "Date of Birth": r"Date Of Birth\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    "Email": r"Email\s*([\w\.\-+]+@[\w\.\-]+)",
    "NIN": r"\bNIN\s*([A-Z0-9]+)",
    "Phone Number": r"Telephone Number\s*([\+\d\s]+)",
    "Type of Passport": r"Type of Passport\s*([\w\s]+)",
    "Bank Name": r"Bank Name\s*([\w\s]+)",
    "Place of Collection": r"Place of Collection\s*([\w\s]+)",
    "Ministry": r"Ministry of\s*([\w\s]+)",
}


def extract_fields_from_text(text):
    extracted = {}
    for field, pattern in FIELDS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        extracted[field] = match.group(1).strip() if match else ""
    return extracted


def find_field_position(page, field_label):
    text_instances = page.search_for(field_label)
    return text_instances[0] if text_instances else None


def create_highlighted_image(page, rect, zoom=2.5):
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    if rect:
        draw = ImageDraw.Draw(img)
        x0 = int(rect.x0 * zoom)
        y0 = int(rect.y0 * zoom)
        x1 = int(rect.x1 * zoom)
        y1 = int(rect.y1 * zoom)
        draw.rectangle([x0, y0, x1, y1], outline="red", width=5)
    return img


def extract_value_by_label(text, label):
    pattern = rf"{re.escape(label)}\s*[:\-]?\s*([^\n]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


st.set_page_config(layout="wide")
st.title("Passport PDF Field Extractor & Highlighter (Editable)")

uploaded_file = st.file_uploader("Upload Passport PDF", type="pdf")
if not uploaded_file:
    st.info("Please upload a PDF file to extract fields.")
    st.stop()

doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
page = doc[0]
page_text = page.get_text()

# Extract all fields
default_fields = extract_fields_from_text(page_text)

# --- Session State for Editable Fields ---
if (
    "editable_fields" not in st.session_state
    or st.session_state.get("last_file") != uploaded_file.name
):
    st.session_state.editable_fields = default_fields.copy()
    st.session_state.last_file = uploaded_file.name
if "highlight_field" not in st.session_state:
    st.session_state.highlight_field = None
if "highlight_rect" not in st.session_state:
    st.session_state.highlight_rect = None

# Layout: PDF on left, fields on right
col1, col2 = st.columns([0.6, 0.4])

with col2:
    st.subheader("Extracted & Editable Fields")
    for field in FIELDS.keys():
        # Editable input for each field
        value = st.text_input(
            field, st.session_state.editable_fields.get(field, ""), key=f"input_{field}"
        )
        st.session_state.editable_fields[field] = value
        # Highlight button
        if st.button("Highlight", key=f"btn_{field}"):
            rect = find_field_position(page, field)
            st.session_state.highlight_field = field
            st.session_state.highlight_rect = rect

    st.markdown("---")
    st.subheader("🔎 Search and Highlight Any Field")
    search_label = st.text_input(
        "Enter field label (as it appears in the PDF):", key="search_label"
    )
    search_value = ""
    if search_label:
        search_value = extract_value_by_label(page_text, search_label)
        st.text_input("Value", search_value, key="search_value")
        if st.button("Highlight Search", key="btn_search"):
            rect = find_field_position(page, search_label)
            st.session_state.highlight_field = search_label
            st.session_state.highlight_rect = rect

with col1:
    st.subheader("PDF Preview")
    img = create_highlighted_image(page, st.session_state.highlight_rect, zoom=2.5)
    if st.session_state.highlight_field:
        st.caption(f"Highlighted: {st.session_state.highlight_field}")
    st.image(img, use_container_width=True)
