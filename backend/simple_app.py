from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
from PIL import Image
import io
import logging
import warnings
from pathlib import Path
from typing import Optional
import tensorflow as tf

class CropData(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    user_id: str = "demo_user"
    language: str = "en"

def generate_crop_advice(crop: str, data: CropData) -> str:
    """Generate customized farming advice based on the crop and soil parameters."""
    
    advice = f"Based on your soil parameters, {crop} is recommended.\n\n"
    
    # NPK advice
    if data.N < 50:
        advice += "- Nitrogen (N) is low. Consider adding nitrogen-rich fertilizers.\n"
    elif data.N > 100:
        advice += "- Nitrogen (N) is high. Reduce nitrogen fertilization.\n"
        
    if data.P < 30:
        advice += "- Phosphorus (P) is low. Add phosphate fertilizers.\n"
    elif data.P > 100:
        advice += "- Phosphorus (P) is high. Reduce phosphate application.\n"
        
    if data.K < 30:
        advice += "- Potassium (K) is low. Add potash fertilizers.\n"
    elif data.K > 100:
        advice += "- Potassium (K) is high. Reduce potassium application.\n"
    
    # pH advice
    if data.ph < 6.0:
        advice += "- Soil is acidic. Consider adding lime to raise pH.\n"
    elif data.ph > 8.0:
        advice += "- Soil is alkaline. Consider adding sulfur to lower pH.\n"
    
    # General care advice
    advice += f"\nGeneral care for {crop}:\n"
    advice += "1. Prepare the soil well before planting\n"
    advice += "2. Maintain proper spacing between plants\n"
    advice += "3. Monitor for pests and diseases regularly\n"
    advice += f"4. Maintain soil moisture appropriate for {crop}\n"
    
    return advice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Filter Python 3.9 deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

app = FastAPI(title="AgriMind.AI API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained crop recommendation model
MODEL_DIR = Path("models")
disease_class_names = {}

try:
    crop_model = joblib.load(MODEL_DIR / 'crop_rf.joblib')
    logger.info("Crop recommendation model loaded successfully")
except Exception as e:
    logger.error(f"Error loading crop model: {e}")
    crop_model = None

try:
    disease_model = tf.keras.models.load_model(MODEL_DIR / "disease_mobilenet.h5")
    logger.info("Disease detection model loaded successfully")
    
    # Load class indices
    class_indices = joblib.load(MODEL_DIR / "disease_classes.joblib")
    disease_class_names = {v: k for k, v in class_indices.items()}
    logger.info(f"Loaded {len(disease_class_names)} disease classes")
    logger.info(f"Sample classes: {list(disease_class_names.values())[:3]}")
except Exception as e:
    logger.error(f"Error loading disease model: {e}")
    logger.error(f"Please run 'python train_models.py' to train the models")
    disease_model = None
    disease_class_names = {}

def parse_disease_class(class_name: str) -> dict:
    """Parse disease class name to extract crop and disease information."""
    parts = class_name.replace('___', '|').replace('__', '|').replace('_', ' ').split('|')
    
    if len(parts) >= 2:
        crop = parts[0].strip()
        disease = parts[1].strip()
        is_healthy = 'healthy' in disease.lower()
        
        return {
            "crop": crop,
            "disease": disease if not is_healthy else "Healthy",
            "is_healthy": is_healthy
        }
    else:
        return {
            "crop": "Unknown",
            "disease": class_name,
            "is_healthy": False
        }

def is_valid_plant_image(confidence: float, threshold: float = 0.3) -> bool:
    """Check if the image is a valid plant image based on confidence score."""
    return confidence >= threshold

@app.post("/recommend_crop")
async def recommend_crop(data: CropData):
    try:
        if crop_model is None:
            raise Exception("Crop recommendation model not loaded")
            
        # Prepare input features
        features = [[
            data.N,
            data.P,
            data.K,
            data.temperature,
            data.humidity,
            data.ph,
            data.rainfall
        ]]
        
        # Make prediction
        predicted_crop = crop_model.predict(features)[0]
        
        # Get probability scores
        probabilities = crop_model.predict_proba(features)[0]
        confidence = float(max(probabilities))
        
        # Generate advice based on the crop and parameters
        advice = generate_crop_advice(predicted_crop, data)
        
        return {
            "success": True,
            "recommended_crop": predicted_crop,
            "confidence": confidence,
            "advice": advice
        }
    except Exception as e:
        logger.error(f"Error in crop recommendation: {e}")
        return {
            "success": False,
            "detail": "Unable to process crop recommendation. Please try again later."
        }

@app.post("/detect_disease")
async def detect_disease(
    file: UploadFile = File(...),
    user_id: Optional[str] = None
):
    if not disease_model or not disease_class_names:
        raise HTTPException(
            status_code=503,
            detail="Disease detection model not available. Please wait for model training to complete or contact support."
        )
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image file."
            )
        
        # Process image
        contents = await file.read()
        
        try:
            img = Image.open(io.BytesIO(contents)).convert('RGB')
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file. Please upload a valid image."
            )
        
        # Resize to match model input
        img = img.resize((160, 160))  # Match training size
        img_array = np.expand_dims(np.array(img) / 255.0, axis=0)
        
        logger.info(f"Processing image with shape: {img_array.shape}")
        
        # Make prediction
        prediction = disease_model.predict(img_array, verbose=0)
        disease_label = int(np.argmax(prediction))
        confidence = float(np.max(prediction))
        
        logger.info(f"Prediction: class={disease_label}, confidence={confidence:.3f}")
        
        # Check if image is valid
        if not is_valid_plant_image(confidence, threshold=0.3):
            raise HTTPException(
                status_code=400,
                detail="Invalid plant image. Please upload a clear image of Tomato, Potato, or Pepper leaf."
            )
        
        # Get class name and parse it
        class_name = disease_class_names.get(disease_label, f"Unknown_{disease_label}")
        logger.info(f"Class name: {class_name}")
        
        disease_info = parse_disease_class(class_name)
        
        crop_name = disease_info["crop"]
        disease_name = disease_info["disease"]
        is_healthy = disease_info["is_healthy"]
        
        # Generate advice
        if is_healthy:
            advice = f"✅ Your {crop_name} plant appears healthy!\n\n"
            advice += "Maintenance tips:\n"
            advice += "1. Continue regular watering schedule\n"
            advice += "2. Ensure adequate sunlight (6-8 hours daily)\n"
            advice += "3. Monitor for early signs of pests or disease\n"
            advice += "4. Maintain good air circulation\n"
            advice += "5. Apply balanced fertilizer as needed"
        else:
            advice = f"⚠️ {disease_name} detected in {crop_name}\n\n"
            advice += "Treatment recommendations:\n"
            advice += "1. Remove and destroy affected leaves\n"
            advice += "2. Apply appropriate fungicide or treatment\n"
            advice += "3. Improve air circulation around plants\n"
            advice += "4. Avoid overhead watering\n"
            advice += "5. Monitor other plants for spread\n\n"
            advice += "Consult a local agricultural expert for specific treatment options."
        
        return {
            "success": True,
            "crop": crop_name,
            "disease": disease_name,
            "is_healthy": is_healthy,
            "confidence": confidence,
            "advice": advice
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in disease detection: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process disease detection: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)