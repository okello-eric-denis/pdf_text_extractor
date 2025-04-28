import re

import fitz  # PyMuPDF
import streamlit as st
from PIL import Image, ImageDraw

FIELDS = {
    "Applicant Name": r"Applicant Name\s*([A-Z\s]+)",
    "Date of Birth": r"Date Of Birth\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    "Email": r"Email\s*([\w\.\-+]+@[\w\.\-]+)",
    "NIN": r"\bNIN\s*([A-Z0-9]+)",
    "Phone Number": r"Telephone Number\s*([\+\d\s]+)",
    "Type of Passport": r"Type of Passport\s*([\w\s]+)",
}


def extract_fields_from_document(doc):
    extracted = {}
    for field, pattern in FIELDS.items():
        found = False
        for i, page in enumerate(doc):
            text = page.get_text()
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[field] = {"value": match.group(1).strip(), "page": i + 1}
                found = True
                break
        if not found:
            extracted[field] = {"value": "", "page": None}
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


def extract_value_by_label(doc, label):
    for i, page in enumerate(doc):
        text = page.get_text()
        pattern = rf"{re.escape(label)}\s*[:\-]?\s*([^\n]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip(), i + 1
    return "", None


st.set_page_config(
    layout="wide",
    page_title="Passport PDF Field Extractor & Highlighter",
    page_icon="🛂",
)
st.title("Passport PDF Field Extractor & Highlighter (Whole Document Search)")

uploaded_file = st.file_uploader("Upload Passport PDF", type="pdf")
if not uploaded_file:
    st.info("Please upload a PDF file to extract fields.")
    st.stop()

doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
num_pages = len(doc)

# --- Session State for Highlight ---
if "highlight_field" not in st.session_state:
    st.session_state.highlight_field = None
if "highlight_rect" not in st.session_state:
    st.session_state.highlight_rect = None
if "highlight_page" not in st.session_state:
    st.session_state.highlight_page = 1

# Extract all fields from the entire document
all_fields = extract_fields_from_document(doc)

# Layout: PDF on left, fields on right
col1, col2 = st.columns([0.6, 0.4])

with col2:
    st.subheader("Extracted & Editable Fields (from whole document)")
    for field in FIELDS.keys():
        info = all_fields[field]
        value = st.text_input(
            f"{field} (Page {info['page'] if info['page'] else '-'})",
            info["value"],
            key=f"input_{field}",
        )
        # Highlight button
        if st.button("Highlight", key=f"btn_{field}"):
            if info["page"]:
                st.session_state.highlight_field = field
                st.session_state.highlight_page = info["page"]
                page = doc[info["page"] - 1]
                rect = find_field_position(page, field)
                st.session_state.highlight_rect = rectimport re

import fitz  # PyMuPDF
import streamlit as st
from PIL import Image, ImageDraw

FIELDS = {
    "Applicant Name": r"Applicant Name\s*([A-Z\s]+)",
    "Date of Birth": r"Date Of Birth\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    "Email": r"Email\s*([\w\.\-+]+@[\w\.\-]+)",
    "NIN": r"\bNIN\s*([A-Z0-9]+)",
    "Phone Number": r"Telephone Number\s*([\+\d\s]+)",
    "Type of Passport": r"Type of Passport\s*([\w\s]+)",
}


def extract_fields_from_document(doc):
    extracted = {}
    for field, pattern in FIELDS.items():
        found = False
        for i, page in enumerate(doc):
            text = page.get_text()
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[field] = {"value": match.group(1).strip(), "page": i + 1}
                found = True
                break
        if not found:
            extracted[field] = {"value": "", "page": None}
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


def extract_value_by_label(doc, label):
    for i, page in enumerate(doc):
        text = page.get_text()
        pattern = rf"{re.escape(label)}\s*[:\-]?\s*([^\n]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip(), i + 1
    return "", None


st.set_page_config(
    layout="wide",
    page_title="Passport PDF Field Extractor & Highlighter",
    page_icon="🛂",
)
st.title("Passport PDF Field Extractor & Highlighter (Whole Document Search)")

uploaded_file = st.file_uploader("Upload Passport PDF", type="pdf")
if not uploaded_file:
    st.info("Please upload a PDF file to extract fields.")
    st.stop()

doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
num_pages = len(doc)

# --- Session State for Highlight ---
if "highlight_field" not in st.session_state:
    st.session_state.highlight_field = None
if "highlight_rect" not in st.session_state:
    st.session_state.highlight_rect = None
if "highlight_page" not in st.session_state:
    st.session_state.highlight_page = 1

# Extract all fields from the entire document
all_fields = extract_fields_from_document(doc)

# Layout: PDF on left, fields on right
col1, col2 = st.columns([0.6, 0.4])

with col2:
    st.subheader("Extracted & Editable Fields (from whole document)")
    for field in FIELDS.keys():
        info = all_fields[field]
        value = st.text_input(
            f"{field} (Page {info['page'] if info['page'] else '-'})",
            info["value"],
            key=f"input_{field}",
        )
        # Highlight button
        if st.button("Highlight", key=f"btn_{field}"):
            if info["page"]:
                st.session_state.highlight_field = field
                st.session_state.highlight_page = info["page"]
                page = doc[info["page"] - 1]
                rect = find_field_position(page, field)
                st.session_state.highlight_rect = rect

    st.markdown("---")
    st.subheader("🔎 Search and Highlight Any Field (whole document)")
    search_label = st.text_input(
        "Enter field label (as it appears in the PDF):", key="search_label"
    )
    search_value, search_page = "", None
    if search_label:
        search_value, search_page = extract_value_by_label(doc, search_label)
        st.text_input("Value", search_value, key="search_value")
        if st.button("Highlight Search", key="btn_search"):
            if search_page:
                st.session_state.highlight_field = search_label
                st.session_state.highlight_page = search_page
                page = doc[search_page - 1]
                rect = find_field_position(page, search_label)
                st.session_state.highlight_rect = rect

with col1:
    # Show the page with the current highlight, or page 1 by default
    page_num = st.session_state.highlight_page or 1
    page = doc[page_num - 1]
    st.subheader(f"PDF Preview (Page {page_num} of {num_pages})")
    img = create_highlighted_image(page, st.session_state.highlight_rect, zoom=2.5)
    if st.session_state.highlight_field:
        st.caption(f"Highlighted: {st.session_state.highlight_field}")
    st.image(img, use_container_width=True)

    # Pagination buttons (optional)
    col_pag1, col_pag2, col_pag3, col_pag4, col_pag5 = st.columns([1, 1, 1, 1, 1])
    with col_pag1:
        if st.button("⏮️ First", use_container_width=True, disabled=page_num == 1):
            st.session_state.highlight_page = 1
            st.session_state.highlight_rect = None
            st.session_state.highlight_field = None
    with col_pag2:
        if st.button("◀️ Previous", use_container_width=True, disabled=page_num == 1):
            st.session_state.highlight_page = max(1, page_num - 1)
            st.session_state.highlight_rect = None
            st.session_state.highlight_field = None
    with col_pag3:
        st.markdown(
            f"<div style='text-align:center; font-weight:bold;'>Page {page_num} / {num_pages}</div>",
            unsafe_allow_html=True,
        )
    with col_pag4:
        if st.button(
            "Next ▶️", use_container_width=True, disabled=page_num == num_pages
        ):
            st.session_state.highlight_page = min(num_pages, page_num + 1)
            st.session_state.highlight_rect = None
            st.session_state.highlight_field = None
    with col_pag5:
        if st.button(
            "Last ⏭️", use_container_width=True, disabled=page_num == num_pages
        ):
            st.session_state.highlight_page = num_pages
            st.session_state.highlight_rect = None
            st.session_state.highlight_field = None


    st.markdown("---")
    st.subheader("🔎 Search and Highlight Any Field (whole document)")
    search_label = st.text_input(
        "Enter field label (as it appears in the PDF):", key="search_label"
    )
    search_value, search_page = "", None
    if search_label:
        search_value, search_page = extract_value_by_label(doc, search_label)
        st.text_input("Value", search_value, key="search_value")
        if st.button("Highlight Search", key="btn_search"):
            if search_page:
                st.session_state.highlight_field = search_label
                st.session_state.highlight_page = search_page
                page = doc[search_page - 1]
                rect = find_field_position(page, search_label)
                st.session_state.highlight_rect = rect

with col1:
    # Show the page with the current highlight, or page 1 by default
    page_num = st.session_state.highlight_page or 1
    page = doc[page_num - 1]
    st.subheader(f"PDF Preview (Page {page_num} of {num_pages})")
    img = create_highlighted_image(page, st.session_state.highlight_rect, zoom=2.5)
    if st.session_state.highlight_field:
        st.caption(f"Highlighted: {st.session_state.highlight_field}")
    st.image(img, use_container_width=True)

    # Pagination buttons (optional)
    col_pag1, col_pag2, col_pag3, col_pag4, col_pag5 = st.columns([1, 1, 1, 1, 1])
    with col_pag1:
        if st.button("⏮️ First", use_container_width=True, disabled=page_num == 1):
            st.session_state.highlight_page = 1
            st.session_state.highlight_rect = None
            st.session_state.highlight_field = None
    with col_pag2:
        if st.button("◀️ Previous", use_container_width=True, disabled=page_num == 1):
            st.session_state.highlight_page = max(1, page_num - 1)
            st.session_state.highlight_rect = None
            st.session_state.highlight_field = None
    with col_pag3:
        st.markdown(
            f"<div style='text-align:center; font-weight:bold;'>Page {page_num} / {num_pages}</div>",
            unsafe_allow_html=True,
        )
    with col_pag4:
        if st.button(
            "Next ▶️", use_container_width=True, disabled=page_num == num_pages
        ):
            st.session_state.highlight_page = min(num_pages, page_num + 1)
            st.session_state.highlight_rect = None
            st.session_state.highlight_field = None
    with col_pag5:
        if st.button(
            "Last ⏭️", use_container_width=True, disabled=page_num == num_pages
        ):
            st.session_state.highlight_page = num_pages
            st.session_state.highlight_rect = None
            st.session_state.highlight_field = None
