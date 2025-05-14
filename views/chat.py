import streamlit as st
import requests
from utils.utils import logout_steps
from streamlit_autorefresh import st_autorefresh

def doctor_patient_chat(api_url, cookie_manager):
    auth_token = st.session_state.auth_token
    try:
        if not st.session_state.get("logged_in", False):
            if not auth_token or auth_token == "rubbish":
                st.error("Authentication token not found. Please log in again.")
                logout_steps(cookie_manager)
                return

            # Validate token before proceeding
            response = requests.post(f"{api_url}/validate-token", headers={"Authorization": f"Bearer {auth_token}"})
            if response.status_code != 200:
                st.error("Invalid or expired token. Please log in again.")
                logout_steps(cookie_manager)
                st.rerun()

            data = response.json()
            if data.get("valid", False):
                st.session_state["logged_in"] = True
                st.session_state["valid"] = True
                st.session_state["user"] = data["user"]["uid"]
                st.session_state["user_data"] = data["user"]
                st.session_state["onboarding_complete"] = data["user"]["onboarding_complete"]
                st.rerun()
            else:
                logout_steps(cookie_manager)
                st.rerun()
    except Exception as e:
        st.error(f"Error: Unable to connect to the server. {str(e)}")
        st.rerun()

    header = st.container()
    header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

    ### Custom CSS for the sticky header
    st.markdown(
        """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: sticky;
            top: 2.875rem;
            background-color: #0e1117;
            z-index: 999;
        }
        div.block-container h1 {
            font-size: 1.25rem !important; 
            margin: 0 !important;
        }
    </style>
        """,
        unsafe_allow_html=True
    )
    
    header.title("Doctor-Patient Chat")
    user_data = st.session_state.get("user_data", {})
    user_type = user_data.get("type", "")
    user_id = user_data.get("uid", "")
    if "selected_chat_id" in st.session_state:
        chat_id = st.session_state.selected_chat_id
    else:
        chat_id = "New Chat"

    # Handle new chat creation
    if chat_id == "New Chat" and user_type == "Patient":
        header.markdown("Start a New Chat<hr style='margin-top: -10px; margin-bottom: 10px'>", unsafe_allow_html=True)
        specialization = st.selectbox("Specialization", [
            "General Practitioner", "Cardiologist", "Dermatologist", 
            "Neurologist", "Pediatrician", "Psychiatrist", "Orthopedic Surgeon", 
            "Radiologist", "Endocrinologist", "Oncologist", "Other"
        ])
        chat_option = st.radio("Choose an option", ["Enter One-Time Code", "Random Doctor"])
        
        if chat_option == "Enter One-Time Code":
            code = st.text_input("Enter Code")
            if st.button("Start Chat") and code:
                with st.status("Starting chat..."):
                    response = requests.post(
                        f"{api_url}/assign-doctor", 
                        json={"patient_id": user_id, "code": code, "specialization": specialization}, 
                        headers={"Authorization": f"Bearer {auth_token}"}
                    )
                    if response.status_code == 200:
                        st.success("Chat started successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid Code or Doctor Unavailable")
        elif chat_option == "Random Doctor":
            if st.button("Find Doctor"):
                with st.status("Finding a doctor..."):
                    response = requests.post(
                        f"{api_url}/assign-doctor",
                        json={"patient_id": user_id, "code": "rubbish", "specialization": specialization},
                        headers={"Authorization": f"Bearer {auth_token}"}
                    )
                    if response.status_code == 200:
                        st.success("Chat started successfully!")
                        data = response.json()
                        chat_id = data["chat_id"]
                        st.session_state.loaded_chats = False
                        st.rerun()
                    else:
                        st.error("No available doctors in your specialization")
    
    elif chat_id == "New Chat" and user_type == "Doctor":
        header.markdown("Start a New Chat<hr style='margin-top: -10px; margin-bottom: 10px'>", unsafe_allow_html=True)

        # Specialization selection
        specializations = [
            "General Practitioner", "Cardiologist", "Dermatologist", 
            "Neurologist", "Pediatrician", "Psychiatrist", "Orthopedic Surgeon", 
            "Radiologist", "Endocrinologist", "Oncologist", "Other"
        ]
        col1, col2 = st.columns([6, 1])

        with col1:
            specialization = st.selectbox("Specialization", specializations)
        


        st.markdown("Generate One-Time Code for a Patient")

        if st.button("Generate Code"):
            if not specialization:
                st.error("Please select a specialization before generating a code.")
            else:
                response = requests.post(
                    f"{api_url}/generate-code", 
                    json={"doctor_id": user_id, "specialization": specialization}, 
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Your one-time code has been generated for **{data['specialization']}**.")
                    st.write("🔹 You can share this code with your patient. They can start a new chat with you using this code.")
                    st.code(data['code'], language="plaintext")
                elif response.status_code == 400:
                    st.error("You are not qualified for the specified specialization.")
                else:
                    st.error("Error generating code. Please try again.")

    # Handle existing chat
    elif chat_id != "New Chat":
        col1, col2 = header.columns([6, 1])
        # Initialize session state for storing messages
        if "messages" not in st.session_state:
            st.session_state.messages = []
        # Set chat title based on user type
        with col1:
            st.markdown(f"<p style='margin-top: 10px'>Chat with {st.session_state.display}</p>", unsafe_allow_html=True)
        with col2:
            if st.button("End Chat", key="end_chat_button", ):
                response = requests.post(f"{api_url}/end-chat", json={"chat_id": chat_id}, headers={"Authorization": f"Bearer {auth_token}"})
                if response.status_code == 200:
                    st.success("Chat ended successfully!")
                    # Clear the messages for this chat from session state
                    if messages in st.session_state:
                        del st.session_state.messages
                    if "chat_list" in st.session_state:
                        st.session_state["chat_list"] = [chat for chat in st.session_state["chat_list"] if chat.get("chat_id") != chat_id]
                    st.session_state["chats_loaded"] = True
                    st.rerun()
                else:
                    st.error("Error ending chat")
            st.markdown("")
                    
        header.markdown("<hr style='margin-top: -15px; margin-bottom: 10px'>", unsafe_allow_html=True)
        
        def get_messages():
            response = requests.get(f"{api_url}/get-messages", params={"chat_id": chat_id}, headers={"Authorization": f"Bearer {auth_token}"})
            return response.json().get("messages", []) if response.status_code == 200 else []

        st_autorefresh(interval=30000, key=f"refresh_{chat_id}")
        messages = get_messages()
        st.session_state.messages = messages
        
        # Display existing messages
        for msg in st.session_state.messages:
            sender_type = "user" if msg["sender"] == user_type else "assistant"
            avatar = "👨‍⚕️" if msg["sender"] == "Doctor" else "🙎"
            with st.chat_message(sender_type, avatar=avatar):
                st.markdown(msg["text"])
        
        # Chat input for new messages
        new_message = st.chat_input("Type a message...")
        if new_message:
            avatar = "👨‍⚕️" if user_type == "Doctor" else "🙎"
            with st.chat_message("user", avatar=avatar):
                st.markdown(new_message)
            new_msg = {"sender": user_id, "text": new_message}
            st.session_state.messages.append(new_msg)
            response = requests.post(
                f"{api_url}/send-message", 
                json={"chat_id": chat_id, "sender": user_id, "text": new_message, "user_type": user_type},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            if response.status_code != 200:
                st.session_state.messages.pop()
                st.error("Error sending message")

def ai_specialist_chat(api_url, cookie_manager):
    auth_token = st.session_state.auth_token
    try:
        if not st.session_state.get("logged_in", False):
            if not auth_token or auth_token == "rubbish":
                st.error("Authentication token not found. Please log in again.")
                logout_steps(cookie_manager)
                return

            # Validate token before proceeding
            response = requests.post(f"{api_url}/validate-token", headers={"Authorization": f"Bearer {auth_token}"})
            if response.status_code != 200:
                st.error("Invalid or expired token. Please log in again.")
                logout_steps(cookie_manager)
                st.rerun()

            data = response.json()
            if data.get("valid", False):
                st.session_state["logged_in"] = True
                st.session_state["valid"] = True
                st.session_state["user"] = data["user"]["uid"]
                st.session_state["user_data"] = data["user"]
                st.session_state["onboarding_complete"] = data["user"]["onboarding_complete"]
                st.rerun()
            else:
                logout_steps(cookie_manager)
                st.rerun()
    except Exception as e:
        st.error(f"Error: Unable to connect to the server. {str(e)}")
        st.rerun()

    header = st.container()
    header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

    ### Custom CSS for the sticky header
    st.markdown(
            """
        <style>
            div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
                position: sticky;
                top: 2.875rem;
                background-color: #0e1117;
                z-index: 999;
            }
            div.block-container h1 {
                font-size: 1.25rem !important; 
                margin: 0;
                margin-top: 1rem;
            }
        </style>
            """,
            unsafe_allow_html=True
        )

    col1, _, col2, col3 = header.columns([6, 2, 4, 2])

    with col1:
        st.title("AI-Specialist Chat")
    user_data = st.session_state.get("user_data", {})
    user_type = user_data.get("type", "")
    user_id = user_data.get("uid", "")

    with col2:
        ai_spec = st.selectbox("Model:", ["Gemini-2.0-Flash", "MedLlama-3-8b"], label_visibility="hidden", help="Select the AI specialist")

    if "selected_chat_id" in st.session_state:
        chat_id = st.session_state.selected_chat_id
    else:
        chat_id = "New Chat"
    
    # Set up chat state
    if "ai_chat_messages" not in st.session_state:
        st.session_state["ai_chat_messages"] = []
        st.session_state["ai_chat_messages_loaded"] = False

    if chat_id == "New Chat":
        header.markdown("<hr style='margin-top: 0'>", unsafe_allow_html=True)
    
    if chat_id != "New Chat":
        with col3:
            st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
            if st.button("End Chat", key="end_chat_button", ):
                response = requests.post(f"{api_url}/end-chat", json={"chat_id": chat_id}, headers={"Authorization": f"Bearer {auth_token}"})
                if response.status_code == 200:
                    st.success("Chat ended successfully!")
                    # Clear the messages for this chat from session state
                    if "ai_chat_messages" in st.session_state:
                        st.session_state["ai_chat_messages"] = []
                    if "ai_chat_list" in st.session_state:
                        st.session_state["ai_chat_list"] = [chat for chat in st.session_state["ai_chat_list"] if chat.get("chat_id") != chat_id]
                    st.session_state.selected_chat_id = "New Chat"
                    st.rerun()
                else:
                    st.error("Failed to end chat. Please try again.")
        header.markdown("<hr style='margin-top: 0'>", unsafe_allow_html=True)
        if not st.session_state.get("ai_chat_messages_loaded", False):
            response = requests.get(f"{api_url}/get-ai-messages", params={"chat_id": chat_id}, headers={"Authorization": f"Bearer {auth_token}"})
            st.session_state["ai_chat_messages"] = response.json().get("messages", []) if response.status_code == 200 else []
            st.session_state["ai_chat_messages_loaded"] = True

        # Display previous messages
        for message in st.session_state.ai_chat_messages:
            sender_type = "user" if message["sender"] == user_id else "assistant"
            with st.chat_message(sender_type):
                st.markdown(message["text"])

    # Chat input
    new_message = st.chat_input("Type a message...")
    
    if new_message:
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(new_message)

        # Prepare for AI response
        with st.chat_message("assistant"):
            ai_message_placeholder = st.empty()
            
            try:
                with requests.post(
                    f"{api_url}/ai-chat",
                    json={
                        "chat_id": chat_id,
                        "sender": user_id,
                        "text": new_message,
                        "user_type": user_type,
                        "model": ai_spec
                    },
                    headers={"Authorization": f"Bearer {auth_token}"},
                    stream=True
                ) as response:
                    
                    if response.status_code == 200:
                        # Get chat_id from headers if it's a new chat
                        new_chat_id = response.headers.get('chat_id')
                        
                        # Stream the response
                        full_response = ""
                        for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
                            if chunk:
                                full_response += chunk
                                # Update the message in real-time
                                ai_message_placeholder.markdown(full_response)
                        
                        st.session_state.ai_chat_messages.append({
                            "sender": user_id,
                            "text": new_message
                        })
                        st.session_state.ai_chat_messages.append({
                            "sender": "AI",
                            "text": full_response
                        })
                        
                        # Check if a new chat ID was created
                        if st.session_state.selected_chat_id == "New Chat" and new_chat_id:
                            st.session_state.selected_chat_id = new_chat_id
                            st.session_state["ai_chat_list"] = []
                            st.session_state["ai_loaded_chats"] = False
                            chat_id = new_chat_id
                            st.rerun()
                            
                    else:
                        error_message = f"Error: {response.status_code} - {response.text}"
                        ai_message_placeholder.error(error_message)
            
            except Exception as e:
                error_message = f"Error: {str(e)}"
                st.error(error_message)