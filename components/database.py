# components/database.py
from datetime import datetime

import streamlit as st
from supabase import Client, create_client

# Initialize the Supabase client
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Function to get the Supabase client from session state
def get_supabase():
    """Get the Supabase client from session state"""
    return st.session_state.get("supabase")


# Function to insert a PDF record with user_id to track ownership
def insert_pdf_record(filename, status, user_id):
    """Insert a record with user_id to track ownership"""
    supabase = get_supabase()
    user_info = st.session_state.get("user_info")
    user_id = user_info.get("id")
    if not supabase:
        st.error("Supabase client not initialized.")
        return None

    data = {
        "filename": filename,
        "status": status,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
    }

    response = supabase.table("pdf_records").insert(data).execute()
    return response.data


# Function to fetch only the current user's PDF records
def fetch_pdf_records(user_id):
    """Fetch only the current user's PDF records"""
    supabase = get_supabase()
    user_info = st.session_state.get("user_info")

    if not user_info or not supabase:
        st.warning("User info or Supabase client missing.")
        return []

    user_id = user_info.get("id")
    response = (
        supabase.table("pdf_records").select("*").eq("user_id", user_id).execute()
    )
    return response.data


# Function to get the current user's subscription details
def get_user_subscription(user_id):
    """Get the current user's subscription details"""
    supabase = get_supabase()
    if not supabase:
        st.error("Supabase client not initialized.")
        return None

    response = (
        supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
    )
    if response.data:
        return response.data[0]
    else:
        # Return free tier by default
        return {"plan": "free", "upload_limit": 5, "valid_until": None}


# Function to get the current user's upload count for the current billing period
def get_user_upload_count(user_id):
    """Get the current user's upload count for the current billing period"""
    supabase = get_supabase()
    if not supabase:
        st.error("Supabase client not initialized.")
        return 0

    response = (
        supabase.table("pdf_records").select("*").eq("user_id", user_id).execute()
    )
    return len(response.data)


# Admin function to reset a user's upload count (called after payment)
def reset_user_uploads(user_id):
    """Reset a user's upload count (called after payment)"""
    supabase = get_supabase()
    if not supabase:
        st.error("Supabase client not initialized.")
        return None

    # This would typically be triggered by a webhook from Stripe
    # For now, we'll just update the subscription's renewal_date
    data = {"last_reset": datetime.now().isoformat()}

    response = (
        supabase.table("subscriptions").update(data).eq("user_id", user_id).execute()
    )
    return response.data
