import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_supabase_auth import login_form, logout_button
from supabase import Client, create_client

from components.pdf_extractor import display_app_content
from components.pricing import packages

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def main():
    try:
        session = login_form(
            url=SUPABASE_URL, apiKey=SUPABASE_KEY, providers=["google"]
        )
    except Exception as e:
        st.error(f"⚠️ Authentication failed: {e}")
        st.stop()

    # If no session, show a login prompt
    if not session:
        st.info("Please log in with your Google account to continue.")

    else:
        # When the User is logged in.
        selection = option_menu(
            menu_title=None,
            options=["HOME", "PRICING"],
            icons=["house", "credit-card"],
            orientation="horizontal",
            default_index=0,
        )
        if selection == "HOME":
            display_app_content()
        if selection == "PRICING":
            packages()
        # Logged-in view
        with st.sidebar:
            user_info = session.get("user", {})
            user_email = user_info.get("email", "unknown")
            user_name = (
                user_info.get("user_metadata", {}).get("full_name")
                or user_info.get("user_metadata", {}).get("name")
                or user_email
            )
            st.success(f"✅ Logged in as: `{user_name}`")
            logout_button()


if __name__ == "__main__":
    main()
