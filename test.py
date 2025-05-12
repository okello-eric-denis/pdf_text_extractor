import tempfile

import streamlit as st
from PyPDF2 import PdfReader
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(
    layout="wide",
    page_title="Home",
    page_icon="🛂",
)


def extract_text_from_pdf(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    text_pages = [page.extract_text() for page in pdf_reader.pages]
    return "\n\n".join(text_pages)


def main():
    st.title("Interactive PDF Viewer with Text Extraction and Highlighting")

    uploaded_pdf = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_pdf is not None:
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_pdf.read())
            tmp_file_path = tmp_file.name

        # Extract text from the saved PDF file
        extracted_text = extract_text_from_pdf(tmp_file_path)

        # Button to activate highlighting mode
        highlight_mode = st.button("Activate Highlighting")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("PDF Viewer")
            pdf_viewer(
                input=tmp_file_path,
                width="100%",
                height=600,
                render_text=True,
            )

        with col2:
            st.subheader("Extracted Text")

            # Show extracted text in a text_area (selectable)
            # When highlight_mode is active, instruct user to select text
            if highlight_mode:
                st.info(
                    "Highlight text in this box and press 'Capture Highlight' below."
                )

            selected_text = st.text_area(
                "Text extracted from PDF", extracted_text, height=600
            )

            # Button to capture selected text highlight from the extracted text area
            if highlight_mode:
                if st.button("Capture Highlight"):
                    # Streamlit text_area does not provide direct access to selected text,
                    # so here we simulate by asking user to input the exact highlighted text manually.
                    # (Because native text selection capture is not possible directly in Streamlit)
                    highlight_input = st.text_input("Paste the highlighted text here:")
                    if highlight_input:
                        st.success(f"Captured highlighted text:\n\n{highlight_input}")
                        # Here you would add logic to sync highlight to PDF viewer (future step)


if __name__ == "__main__":
    main()
