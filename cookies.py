import streamlit as st
from streamlit_cookies_manager import CookieManager

@st.cache_resource
def get_cookie_manager():
    cookies = CookieManager()
    return cookies
