import json
import re
from io import BytesIO

import fitz
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw
from streamlit.components.v1 import html

from components.database import (
    fetch_pdf_records,
    get_user_subscription,
    get_user_upload_count,
    insert_pdf_record,
)
from components.openai_functions import json_data


def extract_text_from_pdf(doc):
    """Extracts text from a PDF document and returns it as a string and a page-wise dictionary."""
    full_text = ""
    text_by_page = {}

    for i, page in enumerate(doc):
        page_text = page.get_text()
        text_by_page[i + 1] = page_text
        full_text += page_text + "\n\n"

    return full_text, text_by_page


def create_highlighted_image(
    page, highlighted_text=None, rect=None, zoom=2.5, selection=None
):
    """Create an image of the PDF page with optional highlighted text or rect."""
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    draw = ImageDraw.Draw(img)

    # Draw rectangle if provided
    if rect:
        x0 = int(rect.x0 * zoom)
        y0 = int(rect.y0 * zoom)
        x1 = int(rect.x1 * zoom)
        y1 = int(rect.y1 * zoom)
        draw.rectangle([x0, y0, x1, y1], outline="red", width=3)

    # Highlight text if provided
    if highlighted_text and highlighted_text.strip():
        text_instances = page.search_for(highlighted_text)
        for inst in text_instances:
            x0 = int(inst.x0 * zoom)
            y0 = int(inst.y0 * zoom)
            x1 = int(inst.x1 * zoom)
            y1 = int(inst.y1 * zoom)
            draw.rectangle([x0, y0, x1, y1], outline="red", width=3)

    # Draw selection rectangle if provided
    if selection:
        x0, y0, x1, y1 = selection
        draw.rectangle([x0, y0, x1, y1], outline="blue", width=2)

    return img


def find_text_position(doc, text, page_num=None):
    """Find position of text in the document. Returns (page_num, rect)."""
    if not text or text.strip() == "":
        return None, None

    text = text.strip()
    pages_to_search = [doc[page_num - 1]] if page_num else doc

    for i, page in enumerate(pages_to_search):
        if page_num:
            current_page = page_num
        else:
            current_page = i + 1

        text_instances = page.search_for(text)
        if text_instances:
            return current_page, text_instances[0]

    return None, None


def get_selection_js(zoom_factor):
    """Returns JavaScript code for handling selection on the PDF image."""
    return f"""
    <script>
    let isSelecting = false;
    let startX, startY;
    const container = window.parent.document.querySelector('.stImage img');
    const zoom = {zoom_factor};
    
    function sendSelection(x0, y0, x1, y1) {{
        // Send coordinates back to Streamlit
        window.parent.streamlitBridge.send(JSON.stringify({{
            'x0': x0/zoom,
            'y0': y0/zoom,
            'x1': x1/zoom,
            'y1': y1/zoom
        }}));
    }}
    
    container.addEventListener('mousedown', (e) => {{
        isSelecting = true;
        const rect = container.getBoundingClientRect();
        startX = e.clientX - rect.left;
        startY = e.clientY - rect.top;
    }});
    
    container.addEventListener('mousemove', (e) => {{
        if (!isSelecting) return;
        const rect = container.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        // Draw temporary selection rectangle
        const selectionDiv = window.parent.document.getElementById('temp-selection');
        if (!selectionDiv) {{
            const div = window.parent.document.createElement('div');
            div.id = 'temp-selection';
            div.style.position = 'absolute';
            div.style.border = '2px dashed blue';
            div.style.pointerEvents = 'none';
            window.parent.document.body.appendChild(div);
        }}
        
        const left = Math.min(startX, currentX) + rect.left;
        const top = Math.min(startY, currentY) + rect.top;
        const width = Math.abs(currentX - startX);
        const height = Math.abs(currentY - startY);
        
        const tempDiv = window.parent.document.getElementById('temp-selection');
        tempDiv.style.left = `${{left}}px`;
        tempDiv.style.top = `${{top}}px`;
        tempDiv.style.width = `${{width}}px`;
        tempDiv.style.height = `${{height}}px`;
    }});
    
    container.addEventListener('mouseup', (e) => {{
        if (!isSelecting) return;
        isSelecting = false;
        
        const rect = container.getBoundingClientRect();
        const endX = e.clientX - rect.left;
        const endY = e.clientY - rect.top;
        
        // Remove temporary selection
        const tempDiv = window.parent.document.getElementById('temp-selection');
        if (tempDiv) tempDiv.remove();
        
        // Only send if selection is meaningful (not just a click)
        if (Math.abs(endX - startX) > 5 && Math.abs(endY - startY) > 5) {{
            sendSelection(
                Math.min(startX, endX),
                Math.min(startY, endY),
                Math.max(startX, endX),
                Math.max(startY, endY)
            );
        }}
    }});
    
    // Handle mouse leaving the container
    container.addEventListener('mouseleave', () => {{
        if (isSelecting) {{
            isSelecting = false;
            const tempDiv = window.parent.document.getElementById('temp-selection');
            if (tempDiv) tempDiv.remove();
        }}
    }});
    </script>
    """


def handle_pdf_selection(doc, page_num, selection_coords, zoom):
    """Convert image selection coordinates to PDF text selection."""
    if not selection_coords or not all(selection_coords):
        return None, None

    x0, y0, x1, y1 = selection_coords
    page = doc[page_num - 1]

    # Convert image coordinates to PDF coordinates
    pdf_x0 = x0 / zoom
    pdf_y0 = y0 / zoom
    pdf_x1 = x1 / zoom
    pdf_y1 = y1 / zoom

    # Create a rect in PDF space
    rect = fitz.Rect(pdf_x0, pdf_y0, pdf_x1, pdf_y1)

    # Get text within the selected rectangle
    selected_text = page.get_textbox(rect)

    if selected_text.strip():
        return selected_text, rect
    return None, None


def display_app_content():
    st.title("Interactive PDF Extractor")
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

    # Initialize session state variables
    if "file_processed" not in st.session_state:
        st.session_state.file_processed = False
    if "current_file_name" not in st.session_state:
        st.session_state.current_file_name = ""
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""
    if "text_by_page" not in st.session_state:
        st.session_state.text_by_page = {}
    if "structured_data" not in st.session_state:
        st.session_state.structured_data = {}
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    if "highlight_text" not in st.session_state:
        st.session_state.highlight_text = ""
    if "highlight_rect" not in st.session_state:
        st.session_state.highlight_rect = None
    if "search_input" not in st.session_state:
        st.session_state.search_input = ""
    if "text_selection" not in st.session_state:
        st.session_state.text_selection = ""
    if "selection_data" not in st.session_state:
        st.session_state.selection_data = None
    if "selection_coords" not in st.session_state:
        st.session_state.selection_coords = None

    # Check if this is a new file
    if st.session_state.current_file_name != uploaded_file.name:
        st.session_state.file_processed = False
        st.session_state.current_file_name = uploaded_file.name
        st.session_state.extracted_text = ""
        st.session_state.text_by_page = {}
        st.session_state.structured_data = {}
        st.session_state.current_page = 1
        st.session_state.highlight_text = ""
        st.session_state.highlight_rect = None
        st.session_state.selection_data = None
        st.session_state.selection_coords = None

    # Process the PDF
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    num_pages = len(doc)

    if not st.session_state.file_processed:
        # Record the upload in database - ONLY ONCE
        insert_pdf_record(uploaded_file.name, "processed", user_id)
        # Cache the extracted text
        full_text, text_by_page = extract_text_from_pdf(doc)
        st.session_state.extracted_text = full_text
        st.session_state.text_by_page = text_by_page
        st.session_state.file_processed = True

    # Function to update highlight from text selection
    def update_highlight_from_text():
        if st.session_state.text_selection and st.session_state.text_selection.strip():
            selected_text = st.session_state.text_selection.strip()
            page_num, rect = find_text_position(doc, selected_text)
            if page_num:
                st.session_state.current_page = page_num
                st.session_state.highlight_text = selected_text
                st.session_state.highlight_rect = rect
                st.experimental_rerun()

    # Function to update highlight from search
    def update_highlight_from_search():
        if st.session_state.search_input and st.session_state.search_input.strip():
            search_text = st.session_state.search_input.strip()
            page_num, rect = find_text_position(doc, search_text)
            if page_num:
                st.session_state.current_page = page_num
                st.session_state.highlight_text = search_text
                st.session_state.highlight_rect = rect
                st.experimental_rerun()
            else:
                st.warning(f"Text '{search_text}' not found in the document.")

    # Main content - Two-column layout
    pdf_col, text_col = st.columns([1, 1])

    with pdf_col:
        st.subheader(
            f"PDF Preview (Page {st.session_state.current_page} of {num_pages})"
        )
        current_page = doc[st.session_state.current_page - 1]

        # Create PDF image with highlighting
        img = create_highlighted_image(
            current_page,
            highlighted_text=st.session_state.highlight_text,
            rect=st.session_state.highlight_rect,
            zoom=2.0,
            selection=st.session_state.get("selection_coords"),
        )
        st.image(img, use_container_width=True)

        # Inject JavaScript for selection handling
        html(get_selection_js(2.0), height=0)

        # Handle selection data from JavaScript
        if st.session_state.get("selection_data"):
            try:
                selection_data = json.loads(st.session_state.selection_data)
                x0, y0 = selection_data["x0"], selection_data["y0"]
                x1, y1 = selection_data["x1"], selection_data["y1"]

                # Store selection coordinates for drawing
                st.session_state.selection_coords = (
                    int(x0 * 2.0),
                    int(y0 * 2.0),
                    int(x1 * 2.0),
                    int(y1 * 2.0),
                )

                # Find text in the selection
                selected_text, rect = handle_pdf_selection(
                    doc, st.session_state.current_page, [x0, y0, x1, y1], 2.0
                )

                if selected_text:
                    st.session_state.highlight_text = selected_text
                    st.session_state.highlight_rect = rect
                    st.session_state.text_selection = selected_text
                    st.experimental_rerun()

            except Exception as e:
                st.error(f"Error processing selection: {e}")
            finally:
                # Clear the selection data to prevent reprocessing
                st.session_state.selection_data = None
                st.session_state.selection_coords = None

        # Page navigation controls
        cols = st.columns([1, 1, 1, 1, 1])
        with cols[0]:
            if st.button(
                "⏮️ First",
                use_container_width=True,
                disabled=st.session_state.current_page == 1,
            ):
                st.session_state.current_page = 1
                st.session_state.highlight_rect = None
                st.session_state.highlight_text = ""
                st.session_state.selection_coords = None
                st.experimental_rerun()
        with cols[1]:
            if st.button(
                "◀️ Prev",
                use_container_width=True,
                disabled=st.session_state.current_page == 1,
            ):
                st.session_state.current_page = max(
                    1, st.session_state.current_page - 1
                )
                st.session_state.highlight_rect = None
                st.session_state.highlight_text = ""
                st.session_state.selection_coords = None
                st.experimental_rerun()
        with cols[2]:
            st.markdown(
                f"<div style='text-align:center; font-weight:bold;'>{st.session_state.current_page}/{num_pages}</div>",
                unsafe_allow_html=True,
            )
        with cols[3]:
            if st.button(
                "Next ▶️",
                use_container_width=True,
                disabled=st.session_state.current_page == num_pages,
            ):
                st.session_state.current_page = min(
                    num_pages, st.session_state.current_page + 1
                )
                st.session_state.highlight_rect = None
                st.session_state.highlight_text = ""
                st.session_state.selection_coords = None
                st.experimental_rerun()
        with cols[4]:
            if st.button(
                "⏭️ Last",
                use_container_width=True,
                disabled=st.session_state.current_page == num_pages,
            ):
                st.session_state.current_page = num_pages
                st.session_state.highlight_rect = None
                st.session_state.highlight_text = ""
                st.session_state.selection_coords = None
                st.experimental_rerun()

    with text_col:
        st.subheader("Extracted Text")

        # Page selector for text
        page_options = ["All Pages"] + [f"Page {i+1}" for i in range(num_pages)]
        selected_page = st.selectbox("Select page to view:", page_options)

        # Text display based on selected page
        if selected_page == "All Pages":
            display_text = st.session_state.extracted_text
        else:
            page_num = int(selected_page.split(" ")[1])
            display_text = st.session_state.text_by_page.get(page_num, "")

        # Text area for displaying and selecting text
        st.text_area(
            "Select text to highlight in PDF:",
            value=display_text,
            height=400,
            key="text_selection",
            on_change=update_highlight_from_text,
        )

        # Search functionality
        st.subheader("🔎 Search Document")
        st.text_input(
            "Search for text in document:",
            key="search_input",
            on_change=update_highlight_from_search,
        )
        if st.button("Search"):
            update_highlight_from_search()

    # Download options
    st.markdown("---")
    st.subheader("Download Options")

    if download_format == "TXT":
        st.download_button(
            "⬇️ Download as Text",
            data=st.session_state.extracted_text,
            file_name=f"{uploaded_file.name.split('.')[0]}.txt",
            mime="text/plain",
        )
    elif download_format == "CSV":
        # Creating a CSV with page number and text columns
        csv_data = pd.DataFrame(
            {
                "Page": [
                    f"Page {page}" for page in st.session_state.text_by_page.keys()
                ],
                "Text": list(st.session_state.text_by_page.values()),
            }
        ).to_csv(index=False)

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

    # Upload history
    records = st.checkbox("I would like to see my upload history?")
    if records:
        st.header("Your Upload History")
        records = fetch_pdf_records(user_id)
        st.dataframe(records if records else "No records found.")
