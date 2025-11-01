from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import time
import requests
import warnings
import logging
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
import json
from pathlib import Path
from typing import Optional, Union
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Filter Python 3.9 deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables
load_dotenv()

# Initialize Firebase with error handling
try:
    cred = credentials.Certificate("firebase-config.json")
    initialize_app(cred)
    db = firestore.client()
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.error(f"Firebase initialization failed: {e}")
    logger.info("Running without Firebase integration")
    db = None

# Initialize Hugging Face
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-xxl"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Initialize text generation pipeline for fallback
try:
    generator = pipeline('text-generation', model='gpt2')
    logger.info("Local text generation model loaded successfully")
except Exception as e:
    logger.warning(f"Could not load local text generation model: {e}")
    generator = None

app = FastAPI(title="AgriMind.AI API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML models with better error handling
MODEL_DIR = Path("models")
crop_model = None  # Will be loaded as RandomForestClassifier
disease_model = None  # Will be loaded as tf.keras.Model
disease_class_names = {}  # Will store disease class names (dict mapping class_id -> class_name)

try:
    crop_model = joblib.load(MODEL_DIR / "crop_rf.joblib")
    logger.info("Crop recommendation model loaded successfully")
except Exception as e:
    logger.error(f"Error loading crop model: {e}")

try:
    # Enable mixed precision for better performance on Apple Silicon
    policy = tf.keras.mixed_precision.Policy('mixed_float16')
    tf.keras.mixed_precision.set_global_policy(policy)
    disease_model = tf.keras.models.load_model(MODEL_DIR / "disease_mobilenet.h5")
    logger.info("Disease detection model loaded successfully")
    
    # Load class indices
    class_indices = joblib.load(MODEL_DIR / "disease_classes.joblib")
    # Reverse the dictionary to get class_id -> class_name mapping
    disease_class_names = {v: k for k, v in class_indices.items()}
    logger.info(f"Loaded {len(disease_class_names)} disease classes")
except Exception as e:
    logger.error(f"Error loading disease model: {e}")

class CropData(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    user_id: str
    language: str = "en"

class ChatRequest(BaseModel):
    message: str
    user_id: str
    language: str = "en"

def query_huggingface(prompt: str) -> str:
    """
    Query Hugging Face model for text generation with fallback options
    """
    try:
        # Try Hugging Face API with retries
        for attempt in range(3):  # Try up to 3 times
            try:
                payload = {
                    "inputs": prompt, 
                    "parameters": {
                        "max_length": 150,
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "do_sample": True
                    }
                }
                response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
                
                if response.status_code == 200:
                    generated_text = response.json()[0]["generated_text"]
                    # Clean and format the response
                    generated_text = generated_text.replace(prompt, "").strip()
                    return generated_text
                    
                elif response.status_code == 429:  # Rate limit
                    logger.warning("Rate limit hit, waiting before retry...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
                else:
                    logger.warning(f"API request failed with status {response.status_code}")
                    break
                    
            except requests.exceptions.Timeout:
                logger.warning("API request timed out, retrying...")
                continue
                
            except Exception as e:
                logger.error(f"API request failed: {e}")
                break
        
        # If API fails, try local model
        if generator:
            try:
                outputs = generator(
                    prompt, 
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.95,
                    do_sample=True
                )
                return outputs[0]["generated_text"].replace(prompt, "").strip()
            except Exception as e:
                logger.error(f"Local model failed: {e}")
        
        # If all fails, return a default response
        logger.warning("Both HF API and local model failed, returning default response")
        return ("I apologize, but I'm having trouble generating a response right now. "
                "Please try again later.")
    except Exception as e:
        logger.error(f"Error in text generation: {e}")
        return ("I apologize, but I'm having trouble generating a response right now. "
                "Please try again later.")

def translate_text(text: str, target_lang: str) -> str:
    """
    Translate text using Hugging Face models
    """
    if target_lang == "en":
        return text
    
    language = "Telugu" if target_lang == "te" else "Hindi"
    prompt = f"Translate to {language}: {text}"
    
    try:
        return query_huggingface(prompt)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text  # Return original text if translation fails

def parse_disease_class(class_name: str) -> dict:
    """
    Parse disease class name to extract crop and disease information.
    Format: Crop___Disease or Crop_Disease
    Example: "Tomato___Late_blight" -> {"crop": "Tomato", "disease": "Late blight", "is_healthy": False}
    """
    # Replace underscores with spaces for better readability
    parts = class_name.replace('___', '|').replace('__', '|').replace('_', ' ').split('|')
    
    if len(parts) >= 2:
        crop = parts[0].strip()
        disease = parts[1].strip()
        is_healthy = 'healthy' in disease.lower()
        
        return {
            "crop": crop,
            "disease": disease if not is_healthy else "Healthy",
            "is_healthy": is_healthy,
            "full_name": class_name
        }
    else:
        # Fallback for unexpected format
        return {
            "crop": "Unknown",
            "disease": class_name,
            "is_healthy": False,
            "full_name": class_name
        }

def is_valid_plant_image(confidence: float, threshold: float = 0.3) -> bool:
    """
    Check if the image is a valid plant image based on confidence score.
    If confidence is too low, it might be an invalid image.
    """
    return confidence >= threshold

@app.post("/recommend_crop")
async def recommend_crop(data: CropData):
    if not crop_model:
        raise HTTPException(status_code=503, detail="Crop recommendation model not available")
    
    try:
        # Make prediction
        X = [[data.N, data.P, data.K, data.temperature, data.humidity, data.ph, data.rainfall]]
        crop = crop_model.predict(X)[0]

        # Generate farming advice using Hugging Face
        prompt = f"""
        As an agricultural expert, provide detailed farming advice for {crop} cultivation with these conditions:
        - Soil nutrients: N={data.N}, P={data.P}, K={data.K}, pH={data.ph}
        - Weather: Temperature={data.temperature}°C, Humidity={data.humidity}%, Rainfall={data.rainfall}mm
        
        Include:
        1. Fertilizer recommendations
        2. Irrigation schedule
        3. Pest control measures
        4. Best practices
        """

        advice = query_huggingface(prompt)
        
        # Translate if needed
        if data.language != "en":
            advice = translate_text(advice, data.language)
            crop = translate_text(crop, data.language)

        # Save to Firebase if available
        if db:
            try:
                db.collection("farmers").document(data.user_id).collection("recommendations").add({
                    "crop": crop,
                    "advice": advice,
                    "soil_data": data.dict(),
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                logger.error(f"Firebase error in crop recommendation: {e}")

        return {
            "recommended_crop": crop,
            "advice": advice,
            "success": True
        }

    except Exception as e:
        logger.error(f"Error in crop recommendation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process crop recommendation. Please try again later."
        )

@app.post("/detect_disease")
async def detect_disease(
    file: UploadFile = File(...),
    user_id: Optional[str] = None,
    language: str = "en"
):
    if not disease_model:
        raise HTTPException(status_code=503, detail="Disease detection model not available")
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image file (JPEG, PNG, etc.)"
            )
        
        # Process image
        contents = await file.read()
        
        try:
            img = Image.open(io.BytesIO(contents)).convert('RGB')
        except Exception as e:
            logger.error(f"Error opening image: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid image file. Please upload a valid image."
            )
        
        img = img.resize((224, 224))
        img_array = np.expand_dims(np.array(img) / 255.0, axis=0)
        
        # Make prediction
        prediction = disease_model.predict(img_array)
        disease_label = int(np.argmax(prediction))
        confidence = float(np.max(prediction))
        
        # Check if image is valid (confidence threshold)
        if not is_valid_plant_image(confidence, threshold=0.3):
            raise HTTPException(
                status_code=400,
                detail="The uploaded image does not appear to be a valid plant leaf image. Please upload a clear image of a plant leaf (Tomato, Potato, or Pepper)."
            )
        
        # Get class name and parse it
        class_name = disease_class_names.get(disease_label, f"Unknown_{disease_label}")
        disease_info = parse_disease_class(class_name)
        
        # Extract crop and disease information
        crop_name = disease_info["crop"]
        disease_name = disease_info["disease"]
        is_healthy = disease_info["is_healthy"]
        
        # Generate appropriate advice based on health status
        if is_healthy:
            prompt = f"""
            As a plant pathologist, provide information about a healthy {crop_name} plant:
            
            1. Confirm the plant appears healthy
            2. Best practices to maintain plant health
            3. Common diseases to watch for in {crop_name}
            4. Preventive care recommendations
            """
        else:
            prompt = f"""
            As a plant pathologist, provide detailed information about {disease_name} in {crop_name}:
            
            1. Disease description and causes
            2. Common symptoms to look for
            3. Treatment recommendations (organic and chemical)
            4. Prevention measures for future crops
            5. Expected recovery timeline
            """
        
        advice = query_huggingface(prompt)
        
        # Translate if needed
        if language != "en":
            advice = translate_text(advice, language)
            crop_name = translate_text(crop_name, language)
            disease_name = translate_text(disease_name, language)
        
        # Save to Firebase if available and user_id provided
        if db and user_id:
            try:
                db.collection("farmers").document(user_id).collection("disease_detections").add({
                    "crop": crop_name,
                    "disease": disease_name,
                    "is_healthy": is_healthy,
                    "confidence": confidence,
                    "advice": advice,
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                logger.error(f"Firebase error in disease detection: {e}")
        
        return {
            "crop": crop_name,
            "disease": disease_name,
            "is_healthy": is_healthy,
            "confidence": confidence,
            "advice": advice,
            "success": True
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in disease detection: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process disease detection. Please try again later."
        )

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Generate response using Hugging Face
        prompt = f"""
        As KrishiGPT, a friendly agricultural assistant helping Indian farmers, 
        respond to this farming question in simple, clear language:
        
        {request.message}
        """
        
        response = query_huggingface(prompt)

        # Translate if needed
        if request.language != "en":
            response = translate_text(response, request.language)

        # Save to Firebase if available
        if db:
            try:
                db.collection("farmers").document(request.user_id).collection("chats").add({
                    "question": request.message,
                    "response": response,
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                logger.error(f"Firebase error in chat: {e}")

        return {
            "response": response,
            "success": True
        }

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process chat request. Please try again later."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)