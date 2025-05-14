import streamlit as st

def logout_steps(cookie_manager):
    st.session_state.clear()
    st.session_state["valid"]= False
    st.session_state["logged_in"] = False
    st.session_state["auth_token"] = "rubbish"
    st.session_state["logged_out"] = True
    cookie_manager.set(
                        "auth_token",
                        "rubbish"
                    )
    print("that",cookie_manager.get("auth_token"))