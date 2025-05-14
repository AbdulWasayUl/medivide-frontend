import streamlit as st
import requests
from utils.utils import logout_steps
import io
from PIL import Image, ImageDraw

# Define the dialog (placed *outside* the main function)
@st.dialog("Diagnosis Result", width="small")
def show_diagnosis_result(result, image_data):
    print("Result:", result)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image.thumbnail([224,224], Image.Resampling.LANCZOS)
    # Draw bounding boxes
    draw = ImageDraw.Draw(image)
    for box in result.get("bounding_boxes", []):
        x1, y1, x2, y2 = box["box_2d"]
        label = box["label"]
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        draw.text((x1, y1 - 10), label, fill="red")

    # Display the annotated image
    st.image(image, use_container_width=True)
    st.markdown("### Diagnosis Result")
    st.write(result.get("diagnosis", "No diagnosis found."))
    if st.button("Get Another Diagnosis"):
        # Reset the input fields
        st.session_state.image_type = None
        st.session_state.instructions = ""
        st.rerun()  # Close the dialog and reset the page

def diagnosis(api_url, cookie_manager):
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

    st.title("Medical Image Diagnosis")

    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="uploaded_image")
    user_type = "doctor"  
    # Primary image type selection
    available_image_types = ["Select the Type", "Eye", "X-Ray", "CT Scan", "MRI", "Other"]
    if user_type == "patient":
        # Restrict patients to non-specialized images only
        available_image_types = ["Select the Type", "Eye", "Other"]

    image_type = st.selectbox("Select the type of image", available_image_types)

    # Dynamic secondary selection based on first choice
    subtype_options = []

    if image_type == "Eye":
        subtype_options = ["Select the Condition", "Cataract", "Glaucoma", "Diabetic Retinopathy (DR)", "Other"]
        if user_type == "patient":
            subtype_options = ["Select the Condition", "Cataract", "Other"]

    elif image_type == "X-Ray":
        subtype_options = ["Select the Condition", "Chest", "Bones", "Other"]
        if user_type == "patient":
            st.warning("You are not authorized to upload X-Ray images.")
            st.stop()

    elif image_type == "CT Scan":
        subtype_options = ["Select the Condition", "Lung", "Liver"]
        if user_type == "patient":
            st.warning("You are not authorized to upload CT Scan images.")
            st.stop()

    elif image_type == "MRI":
        subtype_options = ["Select the Condition", "Brain - Alzheimer’s", "Brain - Tumor", "Spine"]
        if user_type == "patient":
            st.warning("You are not authorized to upload MRI images.")
            st.stop()

    elif image_type == "Other":
        subtype_options = ["Select the Condition", "Skin", "Wound", "Other"]

    elif image_type == "Select the Type":
        subtype_options = ["Select the Condition"]

    # Show second dropdown if authorized
    if subtype_options:
        image_subtype = st.selectbox("Select the specific part or condition", subtype_options)

    # Optional instruction field
    instructions = st.text_area("Provide any additional instructions or details")

    # Submit button
    if st.button("Submit"):
        if uploaded_image is not None and image_type!= "Select the Type" and image_subtype != "Select the Condition":
            files = {"image": uploaded_image.getvalue()}
            data = {"typ": image_type, "sub_type": image_subtype, "instructions": instructions}
            
            try:
                print(data)
                response = requests.post(
                    f"{api_url}/get-diagnosis", 
                    files=files, 
                    data=data,
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                if response.status_code == 200:
                    result = response.json().get("diagnosis", "No result found.")
                    show_diagnosis_result(result, uploaded_image.getvalue()) 
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please upload an image and select the type.")