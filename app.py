import gradio as gr
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simple demo interface for AgriMindAI
def predict_disease(image):
    """Placeholder for disease detection"""
    return "Upload an image of a plant leaf to detect diseases. (Backend integration needed)"

def recommend_crop(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
    """Placeholder for crop recommendation"""
    return f"""
    Based on your input:
    - N: {nitrogen}, P: {phosphorus}, K: {potassium}
    - Temperature: {temperature}°C, Humidity: {humidity}%
    - pH: {ph}, Rainfall: {rainfall}mm
    
    Recommended Crop: Rice (ML model will be integrated)
    """

# Create Gradio interface
with gr.Blocks(title="AgriMindAI - Smart Farming Assistant") as demo:
    gr.Markdown("""
    # 🌾 AgriMindAI - Smart Farming Assistant
    
    AI-powered platform for crop recommendation and plant disease detection.
    
    **Note:** This is a demo interface. Full functionality requires backend integration.
    """)
    
    with gr.Tab("🔍 Disease Detection"):
        gr.Markdown("### Upload a plant image to detect diseases")
        with gr.Row():
            with gr.Column():
                disease_image = gr.Image(type="filepath", label="Upload Plant Image")
                disease_btn = gr.Button("Detect Disease", variant="primary")
            with gr.Column():
                disease_output = gr.Textbox(label="Detection Result", lines=5)
        
        disease_btn.click(
            fn=predict_disease,
            inputs=disease_image,
            outputs=disease_output
        )
    
    with gr.Tab("🌾 Crop Recommendation"):
        gr.Markdown("### Enter your soil and environmental parameters")
        with gr.Row():
            with gr.Column():
                nitrogen = gr.Slider(0, 140, 50, label="Nitrogen (N) mg/kg")
                phosphorus = gr.Slider(0, 140, 50, label="Phosphorus (P) mg/kg")
                potassium = gr.Slider(0, 200, 50, label="Potassium (K) mg/kg")
                ph = gr.Slider(0, 14, 7, label="pH Level")
            with gr.Column():
                temperature = gr.Slider(0, 50, 25, label="Temperature (°C)")
                humidity = gr.Slider(0, 100, 50, label="Humidity (%)")
                rainfall = gr.Slider(0, 300, 100, label="Rainfall (mm)")
                crop_btn = gr.Button("Get Recommendation", variant="primary")
        
        crop_output = gr.Textbox(label="Recommendation", lines=8)
        
        crop_btn.click(
            fn=recommend_crop,
            inputs=[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall],
            outputs=crop_output
        )
    
    with gr.Tab("📊 About"):
        gr.Markdown("""
        ## About AgriMindAI
        
        AgriMindAI is an intelligent farming assistant that uses machine learning to help farmers make better decisions.
        
        ### Features:
        - 🎯 **Crop Recommendation**: ML-based suggestions using Random Forest (99% accuracy)
        - 🔍 **Disease Detection**: MobileNetV2 model for 15 disease classes
        - 💬 **AI Assistant**: Expert farming advice
        - 🗣️ **Multi-language**: English, Hindi, Telugu
        
        ### Technology Stack:
        - **Backend**: FastAPI, Python
        - **ML Models**: TensorFlow, Scikit-learn
        - **Frontend**: Streamlit, Gradio
        - **Models**: MobileNetV2, Random Forest
        
        ### GitHub Repository:
        [https://github.com/abhiyeduru/agrimind](https://github.com/abhiyeduru/agrimind)
        
        ---
        **Note:** This demo version shows the UI. Full ML models require backend deployment.
        """)

if __name__ == "__main__":
    demo.launch()
