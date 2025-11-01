import streamlit as st
import requests
from PIL import Image
import io

# Configure page
st.set_page_config(
    page_title="AgriMind.AI",
    page_icon="🌱",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .stTextInput>div>div>input {
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🌱 AgriMind.AI")
st.subheader("Your Smart Farming Assistant")

# Main navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a service:", 
    ["Crop Recommendation", "Disease Detection"])

if page == "Crop Recommendation":
    st.header("🌾 Crop Recommendation")
    st.write("Enter your soil and environmental parameters to get crop recommendations.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nitrogen = st.number_input("Nitrogen (N) mg/kg", 0, 140, 50)
        phosphorus = st.number_input("Phosphorus (P) mg/kg", 0, 140, 50)
        potassium = st.number_input("Potassium (K) mg/kg", 0, 200, 50)
        temperature = st.number_input("Temperature (°C)", 0.0, 50.0, 25.0)
        
    with col2:
        humidity = st.number_input("Humidity (%)", 0.0, 100.0, 50.0)
        ph = st.number_input("pH", 0.0, 14.0, 7.0)
        rainfall = st.number_input("Rainfall (mm)", 0.0, 300.0, 100.0)
    
    if st.button("Get Recommendation"):
        with st.spinner("Analyzing your soil parameters..."):
            try:
                # Debug: Print the request data
                request_data = {
                    "N": nitrogen,
                    "P": phosphorus,
                    "K": potassium,
                    "temperature": temperature,
                    "humidity": humidity,
                    "ph": ph,
                    "rainfall": rainfall
                }
                st.write("Sending request:", request_data)
                
                response = requests.post(
                    "http://localhost:8000/recommend_crop",
                    json=request_data
                )
                
                # Debug: Print raw response
                st.write("Response status:", response.status_code)
                st.write("Response text:", response.text)
                
                if response.status_code == 200:
                    result = response.json()
                    # Debug: Print parsed result
                    st.write("Parsed result:", result)
                    
                    if result.get('success', False):
                        st.success(f"Recommended Crop: {result['recommended_crop']}")
                        if 'advice' in result:
                            st.info("Farming Advice:")
                            st.write(result['advice'])
                    else:
                        st.error(result.get('detail', 'Failed to get recommendation. Please try again.'))
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Error connecting to the server: {str(e)}")

elif page == "Disease Detection":
    st.header("🔍 Plant Disease Detection")
    st.write("Upload a photo of your plant's leaves for disease detection.")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Detect Disease"):
            with st.spinner("Analyzing image..."):
                try:
                    files = {"file": ("image.jpg", uploaded_file.getvalue(), "image/jpeg")}
                    response = requests.post(
                        "http://localhost:8000/detect_disease",
                        files=files
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success', False):
                            st.success(f"Detected Disease: Disease #{result['disease_label']}")
                            st.success(f"Confidence: {result['confidence']*100:.1f}%")
                            if 'advice' in result:
                                st.info("Disease Information and Treatment:")
                                st.write(result['advice'])
                        else:
                            st.error(result.get('detail', 'Failed to analyze image. Please try again.'))
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error("Error connecting to the server. Make sure the backend is running.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Team AgriMind")