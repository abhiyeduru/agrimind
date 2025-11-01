import streamlit as st
import requests
from PIL import Image
import io

# Configure the page
st.set_page_config(
    page_title="AgriMind.AI - Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTitle {
        font-size: 3rem !important;
        color: #2e7d32 !important;
    }
    .stSubheader {
        font-size: 1.5rem !important;
        color: #388e3c !important;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f1f8e9;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🌾 AgriMind.AI")
st.subheader("Your Smart Farming Assistant")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Welcome to AgriMind.AI! 🌿
    
    AgriMind.AI is your intelligent farming companion that helps you make better agricultural decisions using advanced AI technology.
    
    #### Key Features:
    """)
    
    # Feature boxes
    st.markdown("""
    <div class="feature-box">
        🎯 <b>Smart Crop Recommendations</b><br>
        Get personalized crop suggestions based on your soil conditions and local weather.
    </div>
    
    <div class="feature-box">
        🔍 <b>Plant Disease Detection</b><br>
        Upload plant photos to instantly identify diseases and get treatment advice.
    </div>
    
    <div class="feature-box">
        💬 <b>AI Farming Assistant</b><br>
        Chat with our AI to get expert farming advice and answers to your questions.
    </div>
    
    <div class="feature-box">
        🗣️ <b>Multi-language Support</b><br>
        Available in English, Hindi, and Telugu for better accessibility.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.image("assets/farming.svg", caption="Smart Farming with AI", width="stretch")
    
    # Language selector
    st.sidebar.title("🌐 Language / భాష / भाषा")
    language = st.sidebar.selectbox(
        "Select your preferred language:",
        ["English", "తెలుగు", "हिंदी"],
        index=0
    )
    
    # Quick links
    st.sidebar.title("🔗 Quick Links")
    st.sidebar.markdown("""
    - [Crop Recommendation](/Crop_Recommendation)
    - [Disease Detection](/Disease_Detection)
    - [AI Assistant](/Chat)
    - [My History](/History)
    """)

# Footer
st.markdown("---")
st.markdown("### Get Started 🚀")
st.markdown("""
Choose from the sidebar menu or click one of these options:
""")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🌱 Recommend Crops"):
        st.switch_page("pages/2_🌾_Crop_Recommendation.py")

with col2:
    if st.button("🔬 Detect Diseases"):
        st.switch_page("pages/1_🔍_Disease_Detection.py")

with col3:
    if st.button("💬 Chat with AI"):
        st.switch_page("pages/3_💬_Chat.py")

# Version info
st.sidebar.markdown("---")
st.sidebar.markdown("v1.0.0 | Made with ❤️ by AgriMind Team")