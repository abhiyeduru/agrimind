import os

# Backend URL configuration
# For local development, use localhost
# For production, use the deployed backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# API endpoints
API_ENDPOINTS = {
    "detect_disease": f"{BACKEND_URL}/detect_disease",
    "recommend_crop": f"{BACKEND_URL}/recommend_crop",
    "chat": f"{BACKEND_URL}/chat",
}
