import streamlit as st
from supabase import create_client, Client
import datetime

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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