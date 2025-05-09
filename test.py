import base64

import streamlit as st
import streamlit.components.v1 as components
from pdf2image import convert_from_bytes
from PyPDF2 import PdfReader

st.set_page_config(layout="wide", page_title="PDF Text Highlighter")

st.title("Interactive PDF Text Highlighter")

# --- File Upload ---
pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if pdf_file:
    # --- Extract PDF as image (first page only for demo) ---
    images = convert_from_bytes(pdf_file.read(), first_page=1, last_page=1)
    img = images[0]
    img.save("temp_page.png")
    with open("temp_page.png", "rb") as img_file:
        img_bytes = img_file.read()
    img_base64 = base64.b64encode(img_bytes).decode()

    # --- Extract text ---
    pdf_file.seek(0)
    reader = PdfReader(pdf_file)
    text = reader.pages[0].extract_text()
    lines = text.split("\n") if text else []

    # --- Session state for highlight ---
    if "highlighted" not in st.session_state:
        st.session_state["highlighted"] = None

    col1, col2 = st.columns(2)

    # --- Left: PDF Image ---
    with col1:
        st.markdown("#### PDF Page (Image)")
        # Overlay highlight using a transparent div if a line is selected
        # (In a real app, you'd map text to image coordinates. Here, we just overlay a semi-transparent box for demo.)
        highlight_style = ""
        if st.session_state["highlighted"] is not None:
            highlight_style = """
            <div style='
                position: absolute;
                top: 50px; left: 0;
                width: 100%; height: 40px;
                background: rgba(255,255,0,0.4);
                z-index: 10;
            '></div>
            """
        html_img = f"""
        <div style='position:relative; display:inline-block;'>
            <img src='data:image/png;base64,{img_base64}' style='max-width:100%; border:1px solid #ccc;'/>
            {highlight_style if st.session_state["highlighted"] is not None else ""}
        </div>
        """
        st.markdown(html_img, unsafe_allow_html=True)

    # --- Right: Extracted Text with clickable lines ---
    with col2:
        st.markdown("#### Extracted Text (Click to Highlight)")
        # Render each line as a button for highlight
        for idx, line in enumerate(lines):
            key = f"line_{idx}"
            # Highlight the selected line
            if st.session_state["highlighted"] == idx:
                st.markdown(
                    f"<div style='background:yellow; padding:4px; margin-bottom:2px; border-radius:3px; cursor:pointer;'>{line}</div>",
                    unsafe_allow_html=True,
                )
            else:
                if st.button(line, key=key):
                    st.session_state["highlighted"] = idx

        # Button to clear highlight
        if st.session_state["highlighted"] is not None:
            if st.button("Clear Highlight"):
                st.session_state["highlighted"] = None

    # --- JS for syncing highlight (optional, for future expansion) ---
    # For a real two-way highlight between PDF and text, you'd need a custom Streamlit component with JS/PDF.js.
    # This demo keeps everything in Python for simplicity.

else:
    st.info("Please upload a PDF file to begin.")
