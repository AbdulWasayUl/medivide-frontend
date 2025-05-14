import streamlit as st
import requests
import json

def update_medication(index, field, key):
    st.session_state.medication_data[index][field] = st.session_state[key]

def update_medical_history(index, key):
    st.session_state.medical_history_data[index] = st.session_state[key]

def collect_medical_data():
    medical_history_items = [item for item in st.session_state.medical_history_data if item.strip()]
    
    medications_list = []
    for med in st.session_state.medication_data:
        if med["name"].strip():
            medications_list.append({
                "name": med["name"],
                "dosage": med["dosage"],
                "frequency": med["frequency"]
            })
    
    return {
        "medical_history": medical_history_items,
        "medications": medications_list
    }


@st.dialog("User Profile", width="large")
def profile(api_url):
    # Get auth token from cookies
    auth_token = st.session_state.get("auth_token")
    user_data = st.session_state.get("user_data", {})
    user_type = user_data.get("type", "")
    user_id = user_data.get("uid", "")
    if "profile_loaded" not in st.session_state:
        st.session_state.profile_loaded = False
    with st.spinner("Loading profile..."):
        # Make API request to get user profile
        try:
            if not st.session_state.profile_loaded:
                response = requests.get(
                    f"{api_url}/user-profile/{user_id}", params={"user_type": user_type}, 
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                
                if response.status_code == 200:
                    st.session_state.user_profile = response.json()["profile"]
                    st.session_state.profile_loaded = True
                else:
                    st.error("Failed to load profile. Please try again.")
            
            if st.session_state.profile_loaded:
                user_profile = st.session_state.user_profile
                
                # Display different profile info based on user type
                st.subheader(f"Welcome, {user_data.get('name', 'User')}")
                st.markdown(f"<h3 style='margin-top: -10px;'> Role: {user_type}</h3>", unsafe_allow_html=True)

                st.markdown("<hr style='margin-top: 3px;'>", unsafe_allow_html=True)

                st.markdown(f"You can edit you profile here!", unsafe_allow_html=True)

                if user_type == "Patient":
                    if "medical_history_data" not in st.session_state:
                        st.session_state.medical_history_data = user_profile.get('medical_history')
                        st.session_state.medication_data = user_profile.get('medications')
                    with st.container(border=True):
                        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"], index=["Male", "Female", "Other", "Prefer not to say"].index(user_profile.get('gender')))
                        age = st.number_input("Age", min_value=1, max_value=120, step=1, value=user_profile.get('age'))
                        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, step=0.1, value=user_profile.get('weight'))
                        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, step=0.1, value=user_profile.get('height'))

                        st.markdown("Medical History")
                        i = 0
                        while i < len(st.session_state.medical_history_data):
                            col1, col2 = st.columns([10, 1])
                            with col1:
                                st.text_input(
                                    f"Medical Condition {i+1}", 
                                    value=st.session_state.medical_history_data[i],
                                    key=f"medical_history_{i}",
                                    placeholder="Describe the medical condition, when it was diagnosed, and current status",
                                    on_change=lambda i=i, key=f"medical_history_{i}": update_medical_history(i, key)
                                )
                            with col2:
                                # Only show delete button if there's more than one entry
                                if len(st.session_state.medical_history_data)-1 > i:
                                    st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
                                    if st.button("", key=f"delete_history_{i}", icon=":material/delete:"):
                                        st.session_state.medical_history_data.pop(i)
                            i += 1
                        if st.button("Add Another Medical Condition", icon=":material/add:"):
                            st.session_state.medical_history_data.append("")

                        st.markdown("Medications")
                        i = 0
                        while i < len(st.session_state.medication_data):
                            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                            
                            with col1:
                                name_key = f"medication_name_{i}"
                                st.text_input(
                                    f"Medication Name {i+1}", 
                                    value=st.session_state.medication_data[i]["name"],
                                    key=name_key,
                                    placeholder="Medication name",
                                    on_change=lambda i=i, key=name_key: update_medication(i, "name", key)
                                )
                            
                            with col2:
                                dose_key = f"medication_dose_{i}"
                                st.text_input(
                                    "Dosage", 
                                    value=st.session_state.medication_data[i]["dosage"],
                                    key=dose_key,
                                    placeholder="e.g., 10mg",
                                    on_change=lambda i=i, key=dose_key: update_medication(i, "dosage", key)
                                )
                            
                            with col3:
                                freq_key = f"medication_frequency_{i}"
                                st.text_input(
                                    "Frequency", 
                                    value=st.session_state.medication_data[i]["frequency"],
                                    key=freq_key,
                                    placeholder="e.g., Twice daily",
                                    on_change=lambda i=i, key=freq_key: update_medication(i, "frequency", key)
                                )
                            
                            with col4:
                                # Only show delete button if there's more than one entry
                                if len(st.session_state.medication_data)-1 > i:
                                    st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
                                    if st.button("", key=f"delete_med_{i}", icon=":material/delete:"):
                                        st.session_state.medication_data.pop(i)
                            i += 1
                        
                        if st.button("Add Another Medication", icon=":material/add:"):
                            st.session_state.medication_data.append({"name": "", "dosage": "", "frequency": ""})

                        st.markdown("---")

                        submitted = st.button("Save Changes")

                        if submitted:
                            med_data = collect_medical_data()
                            updated_profile = {
                                "height": height,
                                "weight": weight,
                                "age": age,
                                "gender": gender,
                                "medical_history": med_data["medical_history"],
                                "medications": med_data["medications"]
                            }

                            # Send the updated profile to the backend
                            save_response = requests.put(
                                f"{api_url}/user-profile/{user_id}", json=updated_profile, 
                                headers={"Authorization": f"Bearer {auth_token}"}
                            )

                            if save_response.status_code == 200:
                                st.success("Profile updated successfully!")
                                user_profile = updated_profile
                            else:
                                st.error("Failed to update profile. Please try again.")
                else:
                    if "ot_codes" not in st.session_state:
                        st.session_state.ot_codes = user_profile.get('codes')
                    with st.container(border=True):
                        phone = st.text_input("Phone Number", placeholder="Enter your phone number", value=user_profile.get('phone'))
                        medical_reg_no = st.text_input("Medical Registration Number", placeholder="Enter your registration number", value=user_profile.get('medical_reg_no'))
                        experience = st.number_input("Years of Experience", min_value=0, max_value=70, step=1, value=user_profile.get('experience'))
                        hospital = st.text_input("Hospital/Clinic Name", placeholder="Enter your affiliated hospital/clinic", value=user_profile.get('hospital'))
                        accept_random_patients = st.checkbox("Would you like to be assigned to random patients?", value=user_profile.get('available'))
                        st.markdown("Generated OT Codes")
                        i = 0
                        while i < len(st.session_state.medical_history_data):
                            col1, col2 = st.columns([10, 1])
                            with col1:
                                st.text_input(
                                    "", 
                                    value=st.session_state.ot_codes[i],
                                    key=f"code_{i}",
                                    disabled=True
                                )
                            with col2:
                                # Only show delete button if there's more than one entry
                                st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
                                if st.button("", key=f"delete_code_{i}", icon=":material/delete:"):
                                    st.session_state.ot_codes.pop(i)
                            i += 1
                        st.markdown("---")

                        submitted = st.button("Save Changes")

                        if submitted:
                            codes = st.session_state.ot_codes
                            updated_profile = {
                                "phone": phone,
                                "medical_reg_no": medical_reg_no,
                                "experience": experience,
                                "hospital": hospital,
                                "available": accept_random_patients,
                                "codes": codes
                            }

                            # Send the updated profile to the backend
                            save_response = requests.put(
                                f"{api_url}/user-profile/{user_id}", json=updated_profile, 
                                headers={"Authorization": f"Bearer {auth_token}"}
                            )

                            if save_response.status_code == 200:
                                st.success("Profile updated successfully!")
                            else:
                                st.error("Failed to update profile. Please try again.")
                    

        except Exception as e:
            st.error(f"Error: {str(e)}")