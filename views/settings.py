import streamlit as st
from utils.utils import logout_steps
import requests

@st.dialog("Settings", width="small")
def settings(api_url, cookie_manager):
    # Get auth token from cookies
    auth_token = cookie_manager.get("auth_token")
    print("main", auth_token[:5])
    auth_token = st.session_state.get("auth_token")
    user_data = st.session_state.get("user_data", {})
    user_type = user_data.get("type", "")
    user_id = user_data.get("uid", "")
    user_name = user_data.get('name', 'User')

    st.subheader(f"Welcome, {user_name}")
    st.markdown(f"<h3 style='margin-top: -10px;'> Role: {user_type}</h3>", unsafe_allow_html=True)

    st.markdown("<hr style='margin-top: 3px;'>", unsafe_allow_html=True)

    st.markdown(f"You can edit you profile here!", unsafe_allow_html=True)


    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_name = st.text_input("Change Display Name", value=user_name)
        with col2:
            st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
            if st.button("Update", use_container_width=True):
                try:
                    # API call to update display name
                    response = requests.put(
                        f"{api_url}/users/{user_id}/display-name",
                        headers={"Authorization": f"Bearer {auth_token}"},
                        json={"display_name": new_name}
                    )
                    if response.status_code == 200:
                        # Update session state with new name
                        user_data["name"] = new_name
                        st.session_state.user_data = user_data
                    else:
                        st.error(f"Failed to update display name: {response.json().get('message', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error updating display name: {str(e)}")

    st.markdown("<hr style='margin-top: 10px;'>", unsafe_allow_html=True)
    
    # Chat management section
    st.subheader("Manage Active Chats")

    # Doctor-Patient chats
    with st.container(border=True):
        col1, col2 = st.columns([5,2])

        with col1:
            st.markdown("<div style='font-size:1em; font-weight:normal; margin-top: 7px;'>End All Doctor-Patient Chats</div>", unsafe_allow_html=True)
        with col2:
            if st.button("End All", type="primary", key="end_all_pdchats",use_container_width=True):
                try:
                    response = requests.post(
                        f"{api_url}/end-all-doctor-patient-chats/{user_id}",
                        headers={"Authorization": f"Bearer {auth_token}"}
                    )
                    if response.status_code == 200:
                        st.success("All doctor-patient chats have been ended.")
                    else:
                        st.error(f"Failed to end chats: {response.json().get('message', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error ending doctor-patient chats: {str(e)}")
    
    # AI Specialist chats
    with st.container(border=True):
        col1, col2 = st.columns([5,2])

        with col1:
            st.markdown("<div style='font-size:1em; font-weight:normal; margin-top: 7px;'>End All AI Specialist Chats</div>", unsafe_allow_html=True)
        with col2:
            if st.button("End All", type="primary", key="end_all_aichats", use_container_width=True):
                try:
                    response = requests.post(
                        f"{api_url}/end-all-ai-specialist-chats/{user_id}",
                        headers={"Authorization": f"Bearer {auth_token}"}
                    )
                    if response.status_code == 200:
                        st.session_state["ai_chat_messages"] = []
                        st.session_state["ai_chat_list"] = []
                        st.session_state["ai_loaded_chats"] = False
                        st.success("All AI specialist chats have been ended.")
                    else:
                        st.error(f"Failed to end chats: {response.json().get('message', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error ending AI specialist chats: {str(e)}")
    
    st.markdown("<hr style='margin-top: 10px;'>", unsafe_allow_html=True)
    
    # Security section
    st.subheader("Security Settings")
    _, col, _ = st.columns([2,4,2])
    
    # Reset password
    with col:
        if st.button("Reset Password", type="primary", use_container_width=True, icon=":material/lock_reset:"):
            try:
                response = requests.post(
                    f"{api_url}/reset-password/{user_id}",
                    json={"email": user_data.get("email")},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                if response.status_code == 200:
                    st.success("Password reset email has been sent to your registered email address.")
                else:
                    st.error(f"Failed to initiate password reset: {response.json().get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error resetting password: {str(e)}")
    
    st.markdown("<hr style='margin-top: 10px;'>", unsafe_allow_html=True)
    
    # Logout section
    st.subheader("Session Management")
    _, col, _ = st.columns([2,4,2])
    
    # Reset password
    with col:
        if st.button("Logout", use_container_width=True, icon=":material/logout:"):
            logout_steps(cookie_manager)
            st.rerun()