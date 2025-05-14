# views/onboarding.py
import streamlit as st
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api
from utils.utils import logout_steps

cloudinary.config(
    cloud_name="dpdhc5n4u",
    api_key="361881862949523",
    api_secret="zcWqwsflY1YAutlBLPZMGGUZpwE"
)


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

def patient_onboarding(api_url, cookie_manager):
    st.title("Patient Onboarding")
    
    # Patient-specific onboarding form
    st.subheader("Complete Your Profile")

    if "medical_history_data" not in st.session_state:
        st.session_state.medical_history_data = [""]
    if "medication_data" not in st.session_state:
        st.session_state.medication_data = [{"name": "", "dosage": "", "frequency": ""}]
    
    with st.container(border=True):
        name = st.text_input("Full Name", placeholder="Enter your full name")
        age = st.number_input("Age", min_value=1, max_value=120, step=1)
        gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other", "Prefer not to say"])
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, step=0.1)
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, step=0.1)

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
                        st.rerun()
            i += 1
        if st.button("Add Another Medical Condition", icon=":material/add:"):
            st.session_state.medical_history_data.append("")
            st.rerun()

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
                        st.rerun()
            i += 1
        
        if st.button("Add Another Medication", icon=":material/add:"):
            st.session_state.medication_data.append({"name": "", "dosage": "", "frequency": ""})
            st.rerun()

        st.markdown('---')
        col1, col2 = st.columns([5,1])
        with col1:
            submit_button = st.button("Complete Onboarding")
        with col2:
            st.button("Logout", on_click=logout, args=[cookie_manager], icon=":material/logout:")

    if submit_button:
        # Validation checks
        errors = []
        if not name.strip():
            errors.append("Full Name is required.")
        if gender == "Select":
            errors.append("Please select a gender.")
        if age is None or age < 1:
            errors.append("Age must be a positive number.")
        if weight is None or weight < 1.0:
            errors.append("Weight must be greater than 1 kg.")
        if height is None or height < 50.0:
            errors.append("Height must be greater than 50 cm.")

        if errors:
            for error in errors:
                st.error(error)
            return

        try:
            auth_token = st.session_state.get("auth_token")
            if not auth_token:
                st.error("Authentication token not found. Please log in again.")
                logout_steps(cookie_manager)
                st.rerun()
                

            user_id = st.session_state.get("user")
            if not user_id:
                st.error("User session not found. Please log in again.")
                logout_steps(cookie_manager)
                st.rerun()
            
            med_data = collect_medical_data()

            # Prepare data for API request
            payload = {
                "name": name,
                "age": age,
                "gender": gender,
                "weight": weight,
                "height": height,
                "medical_history": med_data["medical_history"],
                "medications": med_data["medications"]
            }

            response = requests.put(f"{api_url}/patient-onboarding/{user_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})

            if response.status_code == 200:
                st.session_state["onboarding_complete"] = True
                st.success("Profile completed successfully!")
                st.rerun()
            else:
                error_msg = response.json().get("detail", "Error updating profile")
                st.error(f"Error: {error_msg}")
        except Exception as e:
            st.error(f"Error: Unable to connect to the server. {str(e)}")
        
def logout(cookie_manager):
    logout_steps(cookie_manager)
    st.rerun()

def doctor_onboarding(api_url, cookie_manager):
    st.title("Doctor Onboarding")
    
    # Doctor-specific onboarding form
    st.subheader("Complete Your Profile")
    
    with st.container(border=True):
        # Personal Details
        full_name = st.text_input("Full Name", placeholder="Enter your full name")
        phone = st.text_input("Phone Number", placeholder="Enter your phone number")
        
        # Medical Credentials
        specialization = st.multiselect("Specialization", [
            "General Practitioner", "Cardiologist", "Dermatologist", 
            "Neurologist", "Pediatrician", "Psychiatrist", "Orthopedic Surgeon", 
            "Radiologist", "Endocrinologist", "Oncologist", "Other"
        ])
        medical_reg_no = st.text_input("Medical Registration Number", placeholder="Enter your registration number")
        experience = st.number_input("Years of Experience", min_value=0, max_value=70, step=1)
        hospital = st.text_input("Hospital/Clinic Name", placeholder="Enter your affiliated hospital/clinic")
        accept_random_patients = st.checkbox("Would you like to be assigned to random patients?")
        
        # License Upload
        license_file = st.file_uploader("Upload Medical License (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])
        
        # Submit Button
        st.markdown('---')
        col1, col2 = st.columns([5,1])
        with col1:
            submit_button = st.button("Complete Onboarding")
        with col2:
            st.button("Logout", on_click=logout, args=[cookie_manager], icon=":material/logout:")
            

    if submit_button:
        # Validation checks
        errors = []
        if not full_name.strip():
            errors.append("Full Name is required.")
        if not phone.strip():
            errors.append("Phone Number is required.")
        if not specialization:
            errors.append("Please select at least one specialization.")
        if not medical_reg_no.strip():
            errors.append("Medical Registration Number is required.")
        if not license_file:
            errors.append("Medical License upload is required.")

        if errors:
            for error in errors:
                st.error(error)
            return  # Stop execution if validation fails

        try:
            auth_token = st.session_state.get("auth_token")
            if not auth_token:
                st.error("Authentication token not found. Please log in again.")
                logout_steps(cookie_manager)
                st.rerun()
                

            user_id = st.session_state.get("user")
            if not user_id:
                st.error("User session not found. Please log in again.")
                logout_steps(cookie_manager)
                st.rerun()
            
            # Upload License File to Cloudinary
            if license_file:
                # Upload file to Cloudinary
                cloudinary_response = cloudinary.uploader.upload(license_file)
                license_url = cloudinary_response["secure_url"]  # URL of the uploaded image

            # Prepare data for API request
            payload = {
                "full_name": full_name,
                "phone": phone,
                "specialization": specialization,
                "medical_reg_no": medical_reg_no,
                "experience": experience,
                "hospital": hospital,
                "available": accept_random_patients,
                "license_url": license_url,
            }

            response = requests.put(f"{api_url}/doctor-onboarding/{user_id}", json=payload, headers={"Authorization": f"Bearer {auth_token}"})
            
            if response.status_code == 200:
                st.session_state["onboarding_complete"] = True
                st.success("Profile completed successfully! Awaiting verification.")
                st.rerun()
            else:
                error_msg = response.json().get("detail", "Error updating profile")
                st.error(f"Error: {error_msg}")
        except Exception as e:
            st.error(f"Error: Unable to connect to the server. {str(e)}")