import streamlit as st
import fitz
import pandas as pd
from components.openai_functions import json_data
from components.auth import register_user, sign_in_with_google, login_user,logout_user
from components.database import insert_pdf_record, fetch_pdf_records
import json
from streamlit_option_menu import option_menu
from components.pdf_extractor import display_app_content

# --- Authentication UI ---
if "auth" not in st.session_state:
    selection = option_menu(
        menu_title = None,
        options=["HOME", "PRICING", "SIGN IN"],
        icons=["house","credit-card","book"],
        orientation="horizontal",
        default_index=0
    )   
    if selection == "HOME":
        # Display content for the home page
        st.title("Home page")
    if selection == "SIGN IN":
        # Display content for page 1
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
