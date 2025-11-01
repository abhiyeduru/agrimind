import streamlit as st
import requests
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_ENDPOINTS

st.set_page_config(page_title="Crop Recommendation - AgriMind.AI", page_icon="🌾")

st.title("🌾 Smart Crop Recommendation")
st.write("""
Get personalized crop recommendations based on your soil parameters and environmental conditions.
Our AI analyzes multiple factors to suggest the best crop for your field.
""")

# Create two columns for input fields
col1, col2 = st.columns(2)

with col1:
    st.subheader("Soil Parameters")
    nitrogen = st.number_input("Nitrogen (N) mg/kg", 0, 140, 50, help="Amount of nitrogen in soil")
    phosphorus = st.number_input("Phosphorus (P) mg/kg", 0, 140, 50, help="Amount of phosphorus in soil")
    potassium = st.number_input("Potassium (K) mg/kg", 0, 200, 50, help="Amount of potassium in soil")
    ph = st.number_input("pH level", 0.0, 14.0, 7.0, help="Soil pH level")

with col2:
    st.subheader("Environmental Conditions")
    temperature = st.number_input("Temperature (°C)", 0.0, 50.0, 25.0, help="Average temperature")
    humidity = st.number_input("Humidity (%)", 0.0, 100.0, 50.0, help="Average humidity")
    rainfall = st.number_input("Rainfall (mm)", 0.0, 300.0, 100.0, help="Annual rainfall")
    language = st.selectbox("Select Language", ["en", "hi", "te"], index=0)

# Add some spacing
st.write("")

if st.button("Get Recommendation"):
    with st.spinner("Analyzing your parameters..."):
        try:
            # Prepare request data
            request_data = {
                "N": nitrogen,
                "P": phosphorus,
                "K": potassium,
                "temperature": temperature,
                "humidity": humidity,
                "ph": ph,
                "rainfall": rainfall,
                "user_id": "demo_user",
                "language": language
            }
            
            # Debug: Show request data
            st.write("Sending request with data:", request_data)
            
            response = requests.post(
                API_ENDPOINTS["recommend_crop"],
                json=request_data
            )
            
            # Debug: Show raw response
            st.write("Response status code:", response.status_code)
            st.write("Raw response:", response.text)
            
            if response.status_code == 200:
                result = response.json()
                
                # Debug: Show parsed result
                st.write("Parsed response:", result)
                
                if result.get('success', False):
                    # Display results in a nice format
                    st.success(f"🌱 Recommended Crop: {result['recommended_crop']}")
                    
                    # Display advice in an expander
                    with st.expander("View Detailed Farming Advice", expanded=True):
                        st.write(result['advice'])
                    
                    # Display parameter summary
                    with st.expander("Your Input Parameters"):
                        st.json({
                            "Soil Parameters": {
                                "Nitrogen": f"{nitrogen} mg/kg",
                                "Phosphorus": f"{phosphorus} mg/kg",
                                "Potassium": f"{potassium} mg/kg",
                                "pH": ph
                            },
                            "Environmental Conditions": {
                                "Temperature": f"{temperature}°C",
                                "Humidity": f"{humidity}%",
                                "Rainfall": f"{rainfall}mm"
                            }
                        })
                else:
                    st.error(result.get('detail', 'Failed to get recommendation. Please try again.'))
            else:
                st.error(f"Failed to get recommendation. Status code: {response.status_code}")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info(f"Make sure the backend server is running. Current backend URL: {API_ENDPOINTS['recommend_crop']}")