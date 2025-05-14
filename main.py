# main.py

import requests
import streamlit as st
import extra_streamlit_components as stx
from views.landing import landing
from views.dashboard import dashboard
from utils.utils import logout_steps

# Configure the page
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title="Medivise", layout="centered")
    st.session_state["page_config_set"] = True

# Initialize session state
if "logged_out" not in st.session_state:
    st.session_state["logged_out"] = False

# API Endpoint
API_URL = "http://34.57.242.50:8000/api"

# Initialize cookie manager
cookie_manager = stx.CookieManager()

def app():
    auth_token = cookie_manager.get("auth_token")
    # Validate token from cookie if available
    if "logged_in" not in st.session_state:
        # Check if auth token exists in cookies
        auth_token = cookie_manager.get("auth_token")
        
        if auth_token is None or auth_token == "rubbish":
            landing(API_URL, cookie_manager)
        elif st.session_state.get("logged_out", False):
            try:
                # Validate the token
                response = requests.post(
                    f"{API_URL}/validate-token", 
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                data = response.json()
                
                if data.get("valid", False):
                    st.session_state["logged_in"] = True
                    st.session_state["logged_out"] = False
                    st.session_state["valid"] = True
                    st.session_state["user"] = data["user"]["uid"]
                    st.session_state["user_data"] = data["user"]
                    st.session_state["onboarding_complete"] = data["user"]["onboarding_complete"]
                    st.rerun()
                else:
                    logout_steps(cookie_manager)
                    landing(API_URL, cookie_manager)
            except Exception as e:
                logout_steps(cookie_manager)
                landing(API_URL, cookie_manager)
        else:
            landing(API_URL, cookie_manager)
    
    elif not st.session_state.get("logged_in", False):
        landing(API_URL, cookie_manager)
    else:
        dashboard(API_URL, cookie_manager)

if __name__=="__main__":
    app()
