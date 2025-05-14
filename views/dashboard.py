import streamlit as st
from utils.utils import logout_steps
from views.chat import doctor_patient_chat, ai_specialist_chat
from views.onboarding import patient_onboarding, doctor_onboarding
from views.profile import profile
from views.settings import settings
from views.diagnosis import diagnosis
import requests

def dashboard(api_url, cookie_manager):

    user_data = st.session_state.get("user_data", {})
    user_type = user_data.get("type", "")
    user_id = user_data.get("uid", "")

    if user_type == "Doctor":
        verified = user_data.get("verified", True)
        if not verified:
            # Display a styled message for unverified doctors
            st.markdown(
                """
                <div style="
                    text-align: center; 
                    padding: 20px; 
                    border: 1px solid #ff4d4d; 
                    border-radius: 10px; 
                    background-color: rgba(255, 77, 77, 0.1); 
                    color: #ff4d4d; 
                    font-family: 'Arial', sans-serif;
                    margin-bottom: 20px;
                ">
                    <h3 style="margin-bottom: 10px;">Certification Pending Verification</h3>
                    <p style="margin: 0;">Your certification is not verified yet. Please wait until our team verifies your medical practicing certification.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Center the logout button
            col1, col2, col3 = st.columns([3, 1, 3])
            with col2:
                if st.button("Logout", use_container_width=True):
                    logout_steps(cookie_manager)
                    st.rerun()
            return

    # Check if onboarding is required
    if not st.session_state.get("onboarding_complete", False):
        if user_type == "Patient":
            patient_onboarding(api_url, cookie_manager)
        elif user_type == "Doctor":
            doctor_onboarding(api_url, cookie_manager)
            
    else:
        if "auth_token" not in st.session_state:
            st.session_state.loaded_chats = False
            logout_steps(cookie_manager)
            st.rerun()

        auth_token = st.session_state.auth_token

        if "loaded_chats" not in st.session_state:
            st.session_state.loaded_chats = False
        
        if "chat_list" not in st.session_state:
            st.session_state.chat_list = []

        if "ai_loaded_chats" not in st.session_state:
            st.session_state.ai_loaded_chats = False
        
        if "ai_chat_list" not in st.session_state:
            st.session_state.ai_chat_list = []

        if "selected_dialog" not in st.session_state:
            st.session_state.selected_dialog = "none"

        if "selected_chat_id" not in st.session_state:
            st.session_state.selected_chat_id = "New Chat"

        # Sidebar Navigation
        with st.sidebar:
            st.title(f"Welcome, {st.session_state.get('user_data', {}).get('name', '')}")
            st.markdown("<hr style='margin-top: 0.2rem;'>", unsafe_allow_html=True)
            
            dp_expander = st.expander("Doctor-Patient Chat")
            with dp_expander:
                try:
                    if st.session_state.get("loaded_chats", False) == False:
                        # Fetch chats from the backend
                        response = requests.get(
                            f"{api_url}/get-chats",
                            params={"user_id": user_id, "user_type": user_type},
                            headers={"Authorization": f"Bearer {auth_token}"}
                        )
                        
                        if response.status_code == 200:
                            st.session_state.chat_list = response.json().get("chats", [])
                            st.session_state.loaded_chats = True
                        else:
                            st.error("Failed to load chats")
                    # New chat button
                    if st.button("New Chat", key="new_chat_btn", icon=":material/maps_ugc:"):
                        st.session_state.selected_chat_id = "New Chat"
                        st.session_state.selected_page = "Doctor-Patient Chat"
                        st.rerun()

                    chat_list = st.session_state.get("chat_list")
                    
                    # Display chat list
                    st.write("Your Chats:")
                    for chat in chat_list:
                        doctor_name = chat.get("doctor_name", "Unknown Doctor")
                        specialization = chat.get("specialization", "")
                        if user_type == "Patient":
                            chat_display = f"{doctor_name} - {specialization}" 
                        else:
                            patient_name = chat.get("patient_name", "Unknown Patient")
                            patient_id = chat.get("patient_id")
                            chat_display = f"{patient_name} - {patient_id[:5]}"
                            
                        if st.button(chat_display, key=f"chat_{chat.get('chat_id')}", use_container_width=True):
                            st.session_state.selected_chat_id = chat.get('chat_id')
                            st.session_state.display = chat_display
                            st.session_state.selected_page = "Doctor-Patient Chat"
                            st.rerun()
                except Exception as e:
                    st.error(f"Error loading chats: {str(e)}")
            
            # AI Specialist Chat Toggle
            ai_expander = st.expander("AI Specialist Chat")
            with ai_expander:
                try:
                    if st.session_state.get("ai_loaded_chats", False) == False:
                        # Fetch chats from the backend
                        response = requests.get(
                            f"{api_url}/get-ai-chats",
                            params={"user_id": user_id, "user_type": user_type},
                            headers={"Authorization": f"Bearer {auth_token}"}
                        )
                        if response.status_code == 200:
                            st.session_state.ai_chat_list = response.json().get("chats", [])
                            st.session_state.ai_loaded_chats = True
                        else:
                            st.error("Failed to load chats")
                    # New chat button
                    if st.button("New Chat", key="new_ai_chat_btn", icon=":material/maps_ugc:"):
                        st.session_state["ai_chat_messages"] = []
                        st.session_state.selected_chat_id = "New Chat"
                        st.session_state.selected_page = "AI Specialist"
                        st.rerun()

                    chat_list = st.session_state.get("ai_chat_list")
                    
                    # Display chat list
                    st.write("Your Chats:")
                    for chat in chat_list:
                        chat_display = chat.get("chat_id", "New Chat")[-4:]+"-"+chat.get("chat_id", "New Chat")[:15]
                        specialization = chat.get("specialization", "")
                            
                        if st.button(chat_display, key=f"chat_{chat.get('chat_id')}", use_container_width=True):
                            if st.session_state.selected_chat_id != chat.get('chat_id'):
                                st.session_state["ai_chat_messages_loaded"] = False
                            st.session_state.selected_chat_id = chat.get('chat_id')
                            st.session_state.chat = next((c for c in chat_list if c.get("chat_id") == chat.get('chat_id')), None)
                            st.session_state.chat["display"] = chat_display
                            st.session_state.selected_page = "AI Specialist"
                            st.rerun()
                except Exception as e:
                    st.error(f"Error loading chats: {str(e)}")
            
            if st.button("Test / Scan Diagnosis", use_container_width=True):
                st.session_state.selected_page = "Test/Scan Diagnosis"
                st.rerun()

            footer = st.container()
            
            # Add settings and profile icons at the bottom of sidebar
            footer.markdown("---")
            col1, col2, col3, col4 = footer.columns(4)
            with col1:
                if st.button("", help="Profile", icon=":material/person:"):
                    st.session_state.selected_dialog = "profile"
            with col2:
                if st.button("", help="Settings", icon=":material/settings:"):
                    st.session_state.selected_dialog = "settings"
            with col3:
                if st.button("", help="Refresh Chats", icon=":material/source_notes:"):
                    st.session_state.loaded_chats = False
                    st.session_state.ai_loaded_chats = False
                    st.rerun()
            with col4:
                if st.button("", help="Logout", icon=":material/logout:"):
                    logout_steps(cookie_manager)
                    st.rerun()
        
        # Initialize selected_page if not present
        if "selected_page" not in st.session_state:
            st.session_state.selected_page = "Doctor-Patient Chat"
        
        if st.session_state.selected_page == "Doctor-Patient Chat":
            doctor_patient_chat(api_url, cookie_manager)
        elif st.session_state.selected_page == "AI Specialist":
            ai_specialist_chat(api_url, cookie_manager)
        elif st.session_state.selected_page == "Test/Scan Diagnosis":
            diagnosis(api_url, cookie_manager)
        
        if st.session_state.selected_dialog == "settings":
            settings(api_url, cookie_manager)
            st.session_state.selected_dialog = "none"
        elif st.session_state.selected_dialog == "profile":
            profile(api_url)
            st.session_state.selected_dialog = "none"