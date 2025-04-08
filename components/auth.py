import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Initialize Supabase and OpenAI clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def sign_in_with_google():
    try:
        response = supabase.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {
                    "redirectTo": "http://localhost:8501" 
                }
            }
        )
        return response
    except Exception as e:
        return f"Login failed: {str(e)}"


def register_user(email: str, password: str, firstname: str, lastname: str):
    try:
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
