# components/database.py
from datetime import datetime, timedelta

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
        return {"plan": "free", "upload_limit": 10, "valid_until": None}


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


# Function to reset a user's upload count
def reset_user_uploads(user_id):
    """Reset a user's upload count (called after payment)"""
    supabase = get_supabase()
    if not supabase:
        st.error("Supabase client not initialized.")
        return None

    # Update the subscription's last_reset date
    data = {"last_reset": datetime.now().isoformat()}

    response = (
        supabase.table("subscriptions").update(data).eq("user_id", user_id).execute()
    )
    return response.data


def update_user_subscription(user_id, plan, upload_limit):
    """Update a user's subscription plan and upload limit"""
    supabase = get_supabase()
    if not supabase:
        st.error("Supabase client not initialized.")
        return None

    # First check if the user already has a subscription record
    response = (
        supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
    )

    current_time = datetime.now().isoformat()

    # Set valid_until date based on plan type
    valid_until = None
    if plan != "free":
        # Set valid_until to 30 days from now for paid plans
        valid_until = (datetime.now() + timedelta(days=30)).isoformat()

    if response.data:
        # User already has a subscription, update it
        data = {
            "plan": plan,
            "upload_limit": upload_limit,
            "updated_at": current_time,
            "valid_until": valid_until,
        }
        response = (
            supabase.table("subscriptions")
            .update(data)
            .eq("user_id", user_id)
            .execute()
        )
    else:
        # User doesn't have a subscription record, create one
        data = {
            "user_id": user_id,
            "plan": plan,
            "upload_limit": upload_limit,
            "created_at": current_time,
            "updated_at": current_time,
            "last_reset": current_time,
            "valid_until": valid_until,
        }
        response = supabase.table("subscriptions").insert(data).execute()

    return response.data


def check_subscription_validity(user_id):
    """Check if a user's subscription is still valid"""
    supabase = get_supabase()
    if not supabase:
        st.error("Supabase client not initialized.")
        return True  # Default to valid if we can't check

    response = (
        supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
    )

    if not response.data:
        # No subscription record, assume free tier which is always valid
        return True

    subscription = response.data[0]

    # Free plan is always valid
    if subscription.get("plan") == "free":
        return True

    # Check if valid_until date is in the future
    valid_until = subscription.get("valid_until")
    if not valid_until:
        return True  # No expiration date set

    try:
        expiry_date = datetime.fromisoformat(valid_until)
        return expiry_date > datetime.now()
    except (ValueError, TypeError):
        # If date parsing fails, default to valid
        return True
