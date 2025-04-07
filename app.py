import streamlit as st
import fitz
import pandas as pd
import datetime
from supabase import create_client, Client
from openai import OpenAI
import json

# --- CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Initialize Supabase and OpenAI clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)


# --- OpenAI FUNCTION ---
def json_data(extracted_text: str):
    try:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "structure_pdf_content",
                    "description": "Convert unstructured text into structured JSON format",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Document title"},
                            "sections": {"type": "array", "items": {"type": "string", "description": "Section headings"}},
                            "Skills": {"type": "array", "items": {"type": "string", "description": "Key points"}},
                            "experience": {"type": "array", "items": {"type": "string", "description": "Keywords"}},
                            "summary": {"type": "string", "description": "Brief summary"}
                        },
                        "required": ["title", "sections", "key_points", "keywords", "summary"]
                    }
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": """Convert unstructured text into structured JSON with:
                - title
                - sections (array)
                - skills (array)
                - experience (array)
                - summary"""
            },
            {"role": "user", "content": extracted_text}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=tools,
            max_tokens=1000,
            tool_choice="auto"
        )

        if response and response.choices and response.choices[0].message.tool_calls:
            structured_data = response.choices[0].message.tool_calls[0].function.arguments
            return json.loads(structured_data)
        else:
            return {"error": f"Invalid response structure: {response}"}

    except Exception as e:
        return {"error": str(e)}


# --- Authentication Functions ---
def sign_in_with_google():
    try:
        # Initiate the sign-in flow with Google
        response = supabase.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {
                    "redirectTo": "http://localhost:8501"  # Replace with your app's redirect URL
                }
            }
        )
        return response
    except Exception as e:
        return f"Login failed: {str(e)}"


def register_user(email: str, password: str, firstname: str, lastname: str):
    try:
        # Perform sign-up
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "firstname": firstname,
                    "lastname": lastname
                }
            }
        })

        # Access attributes directly
        if response.error:
            return f"Registration failed: {response.error.message}"
        if response.user:
            return "Registration successful! Check your email for verification."

    except Exception as e:
        return f"{str(e)}"


def login_user(email: str, password: str):
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.auth = auth_response

        # Fetch user metadata explicitly
        user_data = supabase.auth.get_user()
        st.session_state.user_metadata = user_data.user.user_metadata

    except Exception as e:
        st.error(f"Login failed: {str(e)}")


def logout_user():
    st.session_state.pop("auth", None)


def insert_pdf_record(filename: str, status: str):
    data = {
        "filename": filename,
        "status": status,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "user_id": st.session_state.auth.user.id
    }
    response = supabase.table("parsed_leases").insert(data).execute()
    return response


def fetch_pdf_records():
    result = supabase.table("parsed_leases").select("*").execute()
    return result.data


def display_app_content():
    # --- Main App UI ---
    st.title("PDF Text Extraction")

    # File Processing Section
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
            if st.session_state.auth:
                display_app_content()


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
                response = sign_in_with_google()
                

    if st.session_state.get("auth"):
        display_app_content()
else:
    # --- Sidebar Logout ---
    name = st.session_state.user_metadata.get('firstname', 'Unknown')
    st.sidebar.header("User Actions")
    st.sidebar.info(f"Logged in as {name}")
    st.sidebar.button("Log out", on_click=logout_user)

    # Display the main content
    display_app_content()
