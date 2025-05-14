# views/signin.py
import streamlit as st
import requests

def login(api_url, cookie_manager):
    st.subheader("Login")
    
    # Use a form to prevent reruns when switching between fields
    with st.form(key="login_form"):
        email = st.text_input("Email *", value="wasay6788@gmail.com")
        password = st.text_input("Password *", type="password", value="Hellogoogle@1")
        
        login_button = st.form_submit_button("Login")
    
    if login_button:
        # Validate required fields
        required_fields = {"Email": email, "Password": password}
        missing_fields = [key for key, value in required_fields.items() if value.strip() == ""]
        if missing_fields:
            message = " \* indicates required fields. Please fill in all fields."
            st.error(message)
            
        else:
            try:
                # Send login request to API
                response = requests.post(
                    f"{api_url}/login", 
                    json={"email": email, "password": password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Store token in cookies
                    cookie_manager.set(
                        "auth_token",
                        data["token"]
                    )
                    print("set")

                    # Update session state
                    st.session_state["logged_in"] = True
                    st.session_state["logged_out"] = False
                    st.session_state["init"]["logged_in"] = True
                    st.session_state["valid"] = True
                    st.session_state["user"] = data["user"]["uid"]
                    st.session_state["user_data"] = data["user"]
                    st.session_state["onboarding_complete"] = data["user"]["onboarding_complete"]
                    st.session_state["auth_token"] = data["token"]
                    st.success("Logged in successfully!")
                else:
                    error_msg = response.json().get("detail", "Invalid email or password")
                    st.error(f"Error: {error_msg}")
            except Exception as e:
                st.error(f"Error: Unable to connect to the server. {str(e)}")