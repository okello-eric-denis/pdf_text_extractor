import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import datetime
from supabase import create_client, Client

# --- CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Authentication Functions ---
def register_user(email: str, password: str):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        return response
    except Exception as e:
        return str(e)

def login_user(email: str, password: str):
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.auth = auth_response
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


# def fetch_pdf_records(user_id: str):
#     response = supabase.table("parsed_leases").select("*").eq("user_id", user_id).execute()
#     return response.data if response.data else []

# records = fetch_pdf_records(user_id)  # Fetch only this user's records


# --- Authentication UI ---
if "auth" not in st.session_state:
    st.title("PDF text Extractor")
    st.text("Please signin to access APP !")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    has_account = st.checkbox("I have an existing account...")

    if has_account:
        if st.button("Login", use_container_width=True):
            login_user(email, password)
    else:
        if st.button("Register", use_container_width=True):
            response = register_user(email, password)
            if isinstance(response, dict):
                st.success("Check your email for verification!")
            else:
                st.error(f"Registration failed: {response}")
    
    st.stop()

# --- Sidebar Logout ---
st.sidebar.header("User Actions")
st.sidebar.info("Logged in as " + st.session_state.auth.user.email)
st.sidebar.button("Log out", on_click=logout_user)
user = st.session_state.auth.user

# --- Main App UI ---
st.title("PDF Text Extraction")

# File Processing Section
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader("📤 Upload PDF Document", type="pdf")

with col2:
    st.caption("Download Options")
    download_format = st.radio("Format:", ["TXT", "CSV"], label_visibility="collapsed")

if uploaded_file:
    with st.spinner("🔍 Extracting text..."):
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            extracted_text = "\n".join([page.get_text() for page in doc])
        st.success("✅ Document processed successfully!")
        insert_pdf_record(uploaded_file.name, "processed")
        
# --- Show extracted Text
        st.text_area("Extracted Content", extracted_text, height=300)

        if download_format == "TXT":
            st.download_button("⬇️ Download as Text", data=extracted_text, file_name=f"{uploaded_file.name.split('.')[0]}.txt", mime="text/plain")
        else:
            csv_data = pd.DataFrame({"Text": [extracted_text]}).to_csv(index=False)
            st.download_button("⬇️ Download as CSV", data=csv_data, file_name=f"{uploaded_file.name.split('.')[0]}.csv", mime="text/csv")
            
records = st.checkbox("I would like to see my upload history?")
if records:
    # Database Records Section ---           
    st.header("Database Records")
    records = fetch_pdf_records()
    st.dataframe(records if records else "No records found.")
            