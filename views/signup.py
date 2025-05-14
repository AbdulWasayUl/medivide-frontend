# views/signup.py
import streamlit as st
import requests

def is_valid_password(password):
    return (
        len(password) >= 10 and
        any(c.islower() for c in password) and
        any(c.isupper() for c in password) and
        any(c.isdigit() for c in password) and
        any(c in "!@#$%^&*()-+" for c in password)
    )

def signup(api_url):
    st.subheader("Sign Up")
    
    with st.form(key="signup_form"):
    # Form inputs
        user_type = st.radio("Select user type:", ["Patient", "Doctor"])
        email = st.text_input("Email *", key="email")
        name = st.text_input("Full Name *", key="name")
        password = st.text_input("Password *", type="password", key="password")
        confirm_password = st.text_input("Confirm Password *", type="password", key="confirm_password")

        register_button = st.form_submit_button("Register")
    

    if register_button:
        # Validate required fields
        required_fields = {"Email": email, "Name": name, "Password": password, "Confirm Password": confirm_password}
        missing_fields = [key for key, value in required_fields.items() if value.strip() == ""]
        if missing_fields:
            st.error("\* indicates required fields. Please fill in all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        elif not is_valid_password(password):
            st.error("Password must be at least 10 characters long, contain at least one uppercase letter, one lowercase letter, one special character, and one digit.")
        else:
            try:
                # Send signup request to API
                response = requests.post(
                    f"{api_url}/signup", 
                    json={
                        "email": email,
                        "password": password,
                        "name": name,
                        "user_type": user_type
                    }
                )
                
                if response.status_code == 200:
                    st.success("Account created successfully! Please log in.")
                else:
                    error_msg = response.json().get("detail", "Error creating account")
                    st.error(f"Error: {error_msg}")
            except Exception as e:
                st.error(f"Error: Unable to connect to the server. {str(e)}")