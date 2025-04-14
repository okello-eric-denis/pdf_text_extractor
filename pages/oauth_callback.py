import streamlit as st

from components.auth import handle_oauth_callback

query_params = st.query_params  # ✅ Get query params from Streamlit
success = handle_oauth_callback(query_params)  # ✅ Assign the result

if success:
    st.success("Authentication successful! Redirecting...")
    if "auth_redirect_origin" in st.session_state:
        redirect_to = st.session_state.auth_redirect_origin
        st.session_state.pop("auth_redirect_origin", None)
        st.switch_page(redirect_to)
    else:
        st.experimental_rerun()
else:
    st.error("Authentication failed. Please try again.")
    if st.button("Back to login"):
        st.switch_page("app.py")
