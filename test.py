import re

import fitz  # PyMuPDF
import streamlit as st
from PIL import Image, ImageDraw


def extract_sections(page_text):
    """Customize this pattern for your document"""
    pattern = r"(?P<header>[A-Z][A-Z\s]+)\n(?P<content>[^\n]+(?:[\s\S]+?)(?=\n[A-Z][A-Z\s]+\n|$))"
    sections = []
    for match in re.finditer(pattern, page_text):
        sections.append(
            {
                "name": match.group("header").strip(),
                "content": match.group("content").strip(),
            }
        )
    return sections


def find_section_position(page, section_name):
    text_instances = page.search_for(section_name)
    return text_instances[0] if text_instances else None


def create_highlighted_image(page, coordinates, zoom=2.0):
    """Generate single high-res image with highlight"""
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    if coordinates:
        draw = ImageDraw.Draw(img)
        x0 = int(coordinates.x0 * zoom)
        y0 = int(coordinates.y0 * zoom)
        x1 = int(coordinates.x1 * zoom)
        y1 = int(coordinates.y1 * zoom)
        draw.rectangle([x0, y0, x1, y1], outline="red", width=5)

    return img


def main():
    st.set_page_config(layout="wide")
    st.title("PDF Field Explorer")

    uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="file_uploader")

    # Reset session state when new file is uploaded
    if uploaded_file and "current_file" not in st.session_state:
        st.session_state.current_file = uploaded_file.name
        st.session_state.current_img = None
    elif uploaded_file and st.session_state.current_file != uploaded_file.name:
        st.session_state.current_file = uploaded_file.name
        st.session_state.current_img = None

    if uploaded_file:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc[0]
        page_text = page.get_text()
        sections = extract_sections(page_text)

        col1, col2 = st.columns([0.6, 0.4])

        with col1:
            st.subheader("Document View")

            # Initialize or update image
            if (
                "current_img" not in st.session_state
                or st.session_state.current_img is None
            ):
                st.session_state.current_img = create_highlighted_image(page, None)

            st.image(st.session_state.current_img, use_container_width=True)

        with col2:
            st.subheader("Available Fields")

            if not sections:
                st.info("No fields detected in document")
                return

            # Display all fields as a list with highlight buttons
            for section in sections:
                with st.expander(f"🔍 {section['name']}", expanded=False):
                    st.text_area(
                        "Content",
                        section["content"],
                        height=100,
                        key=f"content_{section['name']}",
                    )

                    if st.button(
                        f"Highlight {section['name']}", key=f"btn_{section['name']}"
                    ):
                        coordinates = find_section_position(page, section["name"])
                        if coordinates:
                            st.session_state.current_img = create_highlighted_image(
                                page, coordinates
                            )
                            st.rerun()
                        else:
                            st.warning("Field not found on page")


if __name__ == "__main__":
    main()
