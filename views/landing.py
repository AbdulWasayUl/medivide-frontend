import streamlit as st
from streamlit_option_menu import option_menu
from views.signin import login
from views.signup import signup

def landing(API_URL, cookie_manager):
    # Landing Page
    st.title("Welcome to Medivise!")
    st.write("Medivise helps patients and doctors in streamlining the treatment process.")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
    with tab1:
        login(API_URL, cookie_manager)
    
    with tab2:
        signup(API_URL)