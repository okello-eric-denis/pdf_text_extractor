import streamlit as st
import fitz
import pandas as pd
import datetime
from supabase import create_client, Client
from openai import OpenAI
from components.openai_functions import json_data
from components.auth import register_user, sign_in_with_google, login_user,logout_user
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


# --- Authentication UI ---
if "auth" not in st.session_state:
    st.title("PDF text Extractor")
    st.text("Please signin or register to access APP !")
    has_account = st.checkbox("I have an existing account...")

    if has_account:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            login_user(email, password)

    else:
        firstname = st.text_input("First Name")
        lastname = st.text_input("Last Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Register", use_container_width=True):
                response = register_user(email, password, firstname, lastname)
                if isinstance(response, dict):
                    st.success("Check your email for verification!")
                else:
                    st.error(f"Registration failed: {response}")
        with col2:
            if st.button("Sign in with Google", use_container_width=True):
                sign_in_with_google()
                

else:
    # --- Sidebar Logout ---
    name = st.session_state.user_metadata.get('firstname', 'Unknown')
    st.sidebar.header("User Actions")
    st.sidebar.info(f"Logged in as {name}")
    st.sidebar.button("Log out", on_click=logout_user)
    display_app_content()

