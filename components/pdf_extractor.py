import streamlit as st
import fitz
import pandas as pd
from components.openai_functions import json_data
from components.database import insert_pdf_record, fetch_pdf_records
import json

# --Main Application
def display_app_content():
    st.title("PDF Text Extraction")
    col1, col2 = st.columns([3, 1])

    with col1:
        uploaded_file = st.file_uploader("📤 Upload PDF Document", type="pdf")

    with col2:
        st.caption("Download Options")
        download_format = st.radio("Format:", ["TXT", "CSV", "AI JSON SUMMARY"], label_visibility="collapsed")

    if uploaded_file:
        with st.spinner("🔍 Extracting text..."):
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                extracted_text = "\n".join([page.get_text() for page in doc])
            st.success("✅ Document processed successfully!")
            insert_pdf_record(uploaded_file.name, "processed")

            # --- Show extracted Text
            st.text_area("Extracted Content", extracted_text, height=300)

            if download_format == "TXT":
                st.download_button("⬇️ Download as Text", data=extracted_text, file_name=f"{uploaded_file.name.split('.')[0]}.txt",
                                  mime="text/plain")
            elif download_format == "CSV":
                csv_data = pd.DataFrame({"Text": [extracted_text]}).to_csv(index=False)
                st.download_button("⬇️ Download as CSV", data=csv_data, file_name=f"{uploaded_file.name.split('.')[0]}.csv",
                                  mime="text/csv")
            elif download_format == "AI JSON SUMMARY":
                # AI Integration Section for JSON Summary
                with st.spinner("🤖 Structuring content..."):
                    structured_data = json_data(extracted_text)

                if 'error' in structured_data:
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
                        mime="application/json"
                    )

    records = st.checkbox("I would like to see my upload history?")
    if records:
        # Database Records Section ---
        st.header("Database Records")
        records = fetch_pdf_records()
        st.dataframe(records if records else "No records found.")