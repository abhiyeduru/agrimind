import streamlit as st
import requests
import json
import pandas as pd
from PIL import Image
import io
import os
import time
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("../backend/firebase-config.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Constants
API_URL = "http://localhost:8000"
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi"
}

# Page Configuration
st.set_page_config(
    page_title="AgriMind.AI",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .success-message {
        padding: 1rem;
        background-color: #DFF0D8;
        border: 1px solid #3C763D;
        color: #3C763D;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(int(time.time()))  # Simple user ID generation
if 'language' not in st.session_state:
    st.session_state.language = "en"

# Sidebar
with st.sidebar:
    st.title("🌾 AgriMind.AI")
    st.markdown("---")
    
    # Language Selection
    selected_language = st.selectbox(
        "Select Language",
        list(SUPPORTED_LANGUAGES.keys()),
        index=list(SUPPORTED_LANGUAGES.values()).index(st.session_state.language)
    )
    st.session_state.language = SUPPORTED_LANGUAGES[selected_language]
    
    # Navigation
    page = st.radio(
        "Navigate",
        ["Crop Recommendation", "Disease Detection", "AI Chat", "History"]
    )

# Main Content
if page == "Crop Recommendation":
    st.header("🌱 Crop Recommendation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        n = st.number_input("Nitrogen (N)", 0, 140, 50)
        p = st.number_input("Phosphorus (P)", 0, 140, 50)
        k = st.number_input("Potassium (K)", 0, 200, 50)
        ph = st.number_input("pH", 0.0, 14.0, 6.5)
        
    with col2:
        temperature = st.number_input("Temperature (°C)", 0.0, 50.0, 25.0)
        humidity = st.number_input("Humidity (%)", 0.0, 100.0, 70.0)
        rainfall = st.number_input("Rainfall (mm)", 0.0, 300.0, 100.0)
    
    if st.button("Get Recommendation"):
        with st.spinner("Analyzing soil and weather conditions..."):
            try:
                response = requests.post(
                    f"{API_URL}/recommend_crop",
                    json={
                        "N": n,
                        "P": p,
                        "K": k,
                        "temperature": temperature,
                        "humidity": humidity,
                        "ph": ph,
                        "rainfall": rainfall,
                        "user_id": st.session_state.user_id,
                        "language": st.session_state.language
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Recommended Crop: {result['recommended_crop']}")
                    st.markdown("### Detailed Advice:")
                    st.write(result['advice'])
                else:
                    st.error("Failed to get recommendation. Please try again.")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

elif page == "Disease Detection":
    st.header("🔍 Plant Disease Detection")
    
    uploaded_file = st.file_uploader("Upload a leaf image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Detect Disease"):
            with st.spinner("Analyzing image..."):
                try:
                    files = {"file": ("image.jpg", uploaded_file, "image/jpeg")}
                    response = requests.post(
                        f"{API_URL}/detect_disease",
                        files=files,
                        data={
                            "user_id": st.session_state.user_id,
                            "language": st.session_state.language
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Confidence: {result['confidence']*100:.1f}%")
                        st.markdown("### Analysis & Treatment:")
                        st.write(result['advice'])
                    else:
                        st.error("Failed to analyze image. Please try again.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

elif page == "AI Chat":
    st.header("💬 Chat with KrishiGPT")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask your farming question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "message": prompt,
                            "user_id": st.session_state.user_id,
                            "language": st.session_state.language
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.markdown(result['response'])
                        st.session_state.messages.append(
                            {"role": "assistant", "content": result['response']}
                        )
                    else:
                        st.error("Failed to get response. Please try again.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

elif page == "History":
    st.header("📚 Your History")
    
    # Get user's history from Firebase
    try:
        # Get crop recommendations
        recommendations = db.collection("farmers").document(st.session_state.user_id)\
            .collection("recommendations").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5).stream()
        
        st.subheader("Recent Crop Recommendations")
        for rec in recommendations:
            data = rec.to_dict()
            with st.expander(f"Recommendation from {data['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"**Recommended Crop:** {data['crop']}")
                st.write("**Advice:**")
                st.write(data['advice'])
        
        # Get disease detections
        detections = db.collection("farmers").document(st.session_state.user_id)\
            .collection("disease_detections").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5).stream()
        
        st.subheader("Recent Disease Detections")
        for det in detections:
            data = det.to_dict()
            with st.expander(f"Detection from {data['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"**Confidence:** {data['confidence']*100:.1f}%")
                st.write("**Analysis & Treatment:**")
                st.write(data['advice'])
        
        # Get chat history
        chats = db.collection("farmers").document(st.session_state.user_id)\
            .collection("chats").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
        
        st.subheader("Recent Chats")
        for chat in chats:
            data = chat.to_dict()
            with st.expander(f"Chat from {data['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                st.write("**Question:**")
                st.write(data['question'])
                st.write("**Response:**")
                st.write(data['response'])
                
    except Exception as e:
        st.error(f"Failed to load history: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ by AgriMind.AI Team | "
    "🌾 Empowering farmers with AI technology"
)