# components/pdf_extractor.py
import json
import re

import fitz
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw

from components.database import (
    fetch_pdf_records,
    get_user_subscription,
    get_user_upload_count,
    insert_pdf_record,
)
from components.openai_functions import json_data

# Specific regex patterns for each field
FIELDS = {
    "Applicant Name": r"Applicant Name\s*([A-Z\s]+)",
    "Date of Birth": r"Date Of Birth\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    "Email": r"Email\s*([\w\.\-+]+@[\w\.\-]+)",
    "NIN": r"\bNIN\s*([A-Z0-9]+)",
    "Telephone Number": r"Telephone Number\s*([\+\d\s]+)",
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
        draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
    return img


def extract_value_by_label(doc, label):
    for i, page in enumerate(doc):
        text = page.get_text()
        pattern = rf"{re.escape(label)}\s*[:\-]?\s*([^\n]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip(), i + 1
    return "", None


def extract_text_from_pdf(doc):
    """Extracts text from a PDF document and returns it as a string."""
    return "\n".join([page.get_text() for page in doc])


def display_app_content():
    st.title("PDF Text Extraction")
    user_info = st.session_state.get("user_info", {})
    user_id = user_info.get("id", "no-user")
    st.write(f"Hello, {user_info.get('name', 'Guest')} (ID: {user_id})")
    subscription = get_user_subscription(user_id)
    upload_count = get_user_upload_count(user_id)
    uploads_remaining = subscription["upload_limit"] - upload_count

    st.sidebar.subheader("Your Subscription")
    st.sidebar.write(f"**Plan:** {subscription['plan'].capitalize()}")
    st.sidebar.write(f"**Uploads:** {upload_count}/{subscription['upload_limit']}")
    st.sidebar.progress(upload_count / subscription["upload_limit"])
    st.sidebar.write("**Valid Until:**")

    col1, col2 = st.columns([3, 1])

    with col1:
        if uploads_remaining <= 0:
            st.error("⚠️ You've reached your upload limit. Please upgrade your plan.")
            uploaded_file = None
        else:
            st.write(f"You have {uploads_remaining} uploads remaining.")
            uploaded_file = st.file_uploader("📤 Upload PDF Document", type="pdf")

    with col2:
        st.caption("Download Options")
        download_format = st.radio(
            "Format:", ["TXT", "CSV", "AI JSON SUMMARY"], label_visibility="collapsed"
        )

    if not uploaded_file:
        st.info("Please upload a PDF file to extract text.")
        st.stop()

    # Initialize session state for file processing
    if "file_processed" not in st.session_state:
        st.session_state.file_processed = False

    if "current_file_name" not in st.session_state:
        st.session_state.current_file_name = ""

    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""

    if "structured_data" not in st.session_state:
        st.session_state.structured_data = {}

    # Check if this is a new file
    if st.session_state.current_file_name != uploaded_file.name:
        st.session_state.file_processed = False
        st.session_state.current_file_name = uploaded_file.name
        st.session_state.extracted_text = ""
        st.session_state.structured_data = {}

    # Only process and upload to database once per file
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    if not st.session_state.file_processed:
        # Record the upload in database - ONLY ONCE
        insert_pdf_record(uploaded_file.name, "processed", user_id)
        # Cache the extracted text
        st.session_state.extracted_text = extract_text_from_pdf(doc)
        st.session_state.file_processed = True

    num_pages = len(doc)

    # --- Session State for Highlight ---
    if "highlight_field" not in st.session_state:
        st.session_state.highlight_field = None
    if "highlight_rect" not in st.session_state:
        st.session_state.highlight_rect = None
    if "highlight_page" not in st.session_state:
        st.session_state.highlight_page = 1

    all_fields = extract_fields_from_document(doc)

    col1, col2 = st.columns([0.6, 0.4])
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
            if st.button(
                "◀️ Previous", use_container_width=True, disabled=page_num == 1
            ):
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
    with col2:
        st.subheader("Extracted Fields")
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
    # --- End of Session State for Highlight ---

    if download_format == "TXT":
        st.download_button(
            "⬇️ Download as Text",
            data=st.session_state.extracted_text,
            file_name=f"{uploaded_file.name.split('.')[0]}.txt",
            mime="text/plain",
        )
    elif download_format == "CSV":
        csv_data = pd.DataFrame({"Text": [st.session_state.extracted_text]}).to_csv(
            index=False
        )
        st.download_button(
            "⬇️ Download as CSV",
            data=csv_data,
            file_name=f"{uploaded_file.name.split('.')[0]}.csv",
            mime="text/csv",
        )
    elif download_format == "AI JSON SUMMARY":
        # Use cached AI processing results if available
        if not st.session_state.structured_data:
            with st.spinner("🤖 Structuring content..."):
                st.session_state.structured_data = json_data(
                    st.session_state.extracted_text
                )

        structured_data = st.session_state.structured_data

        if "error" in structured_data:
            st.error(f"AI Processing Failed: {structured_data['error']}")
        else:
            st.success("✅ Content Restructured Successfully!")
            # Display structured JSON
            json_preview = st.checkbox("I would like to preview AI Json Summary?")
            if json_preview:
                st.json(structured_data)
            # Provide download option for JSON summary
            json_output = json.dumps(structured_data, indent=2)
            st.download_button(
                label="⬇️ Download as AI JSON Summary",
                data=json_output,
                file_name=f"{uploaded_file.name.split('.')[0]}_summary.json",
                mime="application/json",
            )

    records = st.checkbox("I would like to see my upload history?")
    if records:
        st.header("Your Upload History")
        records = fetch_pdf_records(user_id)
        st.dataframe(records if records else "No records found.")
