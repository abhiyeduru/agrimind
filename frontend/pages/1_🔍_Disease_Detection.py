import streamlit as st
import requests
from PIL import Image
import io
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_ENDPOINTS

st.set_page_config(page_title="Disease Detection - AgriMind.AI", page_icon="🔍")

st.title("🔍 Plant Disease Detection")
st.write("""
Upload a photo of your plant's leaves and our AI will analyze it for diseases.
We can detect various diseases in crops like tomatoes, potatoes, and peppers.
""")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
language = st.selectbox("Select Language", ["en", "hi", "te"], index=0)

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    if st.button("Detect Disease"):
        with st.spinner("Analyzing image..."):
            try:
                # Prepare the file for upload
                files = {"file": ("image.jpg", uploaded_file.getvalue(), "image/jpeg")}
                response = requests.post(
                    API_ENDPOINTS["detect_disease"],
                    files=files,
                    data={"user_id": "demo_user", "language": language}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display crop name prominently
                    st.success(f"## 🌱 Detected Crop: {result.get('crop', 'Unknown')}")
                    
                    # Show health status
                    is_healthy = result.get('is_healthy', False)
                    if is_healthy:
                        st.success(f"### ✅ Status: {result.get('disease', 'Healthy')}")
                        st.balloons()
                    else:
                        st.warning(f"### ⚠️ Disease Detected: {result.get('disease', 'Unknown')}")
                    
                    # Create columns for confidence and advice
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        confidence = result.get('confidence', 0)
                        st.metric("Confidence", f"{confidence*100:.1f}%")
                        
                        # Show color-coded confidence
                        if confidence >= 0.8:
                            st.success("High Confidence")
                        elif confidence >= 0.5:
                            st.info("Medium Confidence")
                        else:
                            st.warning("Low Confidence")
                    
                    with col2:
                        st.info("### 💡 Treatment Advice")
                        st.write(result.get('advice', 'No advice available'))
                    
                    # Additional information in expandable sections
                    with st.expander("📋 General Prevention Tips"):
                        st.write("""
                        **Good Agricultural Practices:**
                        1. Practice crop rotation to prevent soil-borne diseases
                        2. Maintain proper plant spacing for air circulation
                        3. Keep the field clean and remove infected plant debris
                        4. Use disease-resistant varieties when available
                        5. Monitor plants regularly for early detection
                        6. Avoid overhead watering to reduce leaf wetness
                        7. Apply mulch to prevent soil splash onto leaves
                        """)
                    
                    if not is_healthy:
                        with st.expander("🚨 When to Seek Expert Help"):
                            st.write("""
                            Consult an agricultural expert if:
                            - Disease spreads rapidly despite treatment
                            - Multiple plants are affected
                            - You're unsure about treatment application
                            - Organic treatment options are preferred
                            - Large-scale crop management is needed
                            """)
                
                elif response.status_code == 400:
                    # Handle invalid image errors
                    error_detail = response.json().get('detail', 'Invalid image')
                    st.error(f"❌ {error_detail}")
                    st.info("""
                    **Please ensure:**
                    - Image is clear and well-lit
                    - Shows plant leaves (not whole plant)
                    - Is of Tomato, Potato, or Pepper plant
                    - File is a valid image format (JPG, PNG)
                    """)
                else:
                    st.error("Failed to analyze image. Please try again.")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to the server!")
                st.info(f"Please make sure the backend server is running. Backend URL: {API_ENDPOINTS['detect_disease']}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please try uploading a different image or restart the application.")