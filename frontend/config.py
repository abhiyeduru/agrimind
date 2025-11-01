import os
import streamlit as st

# Backend URL configuration
# For local development, use localhost
# For production, use the deployed backend URL from secrets or environment
def get_backend_url():
    # First try to get from Streamlit secrets
    try:
        return st.secrets.get("BACKEND_URL", "http://localhost:8000")
    except:
        # Fall back to environment variable
        return os.getenv("BACKEND_URL", "http://localhost:8000")

BACKEND_URL = get_backend_url()

# API endpoints
API_ENDPOINTS = {
    "detect_disease": f"{BACKEND_URL}/detect_disease",
    "recommend_crop": f"{BACKEND_URL}/recommend_crop",
    "chat": f"{BACKEND_URL}/chat",
}
