import joblib
import tensorflow as tf
import numpy as np
from pathlib import Path
from PIL import Image
import os

def test_crop_recommendation():
    print("\nTesting Crop Recommendation Model...")
    try:
        # Load the model
        model = joblib.load('models/crop_rf.joblib')
        print("Model loaded successfully")
        
        # Test data (example values)
        test_data = [
            [90, 40, 40, 25, 80, 6.5, 200],  # Sample soil and weather conditions
            [60, 30, 35, 28, 70, 7.0, 150],
            [120, 50, 45, 23, 75, 6.8, 180]
        ]
        
        # Make predictions
        for i, data in enumerate(test_data, 1):
            prediction = model.predict([data])[0]
            print(f"\nTest Case {i}:")
            print(f"Input: N={data[0]}, P={data[1]}, K={data[2]}, temp={data[3]}°C, humidity={data[4]}%, pH={data[5]}, rainfall={data[6]}mm")
            print(f"Recommended Crop: {prediction}")
            
        return True
    except Exception as e:
        print(f"Error testing crop recommendation model: {e}")
        return False

def test_disease_detection():
    print("\nTesting Disease Detection Model...")
    try:
        # Load the model
        model = tf.keras.models.load_model('models/disease_mobilenet.h5')
        class_indices = joblib.load('models/disease_classes.joblib')
        print("Model and class indices loaded successfully")
        
        # Get list of test images from PlantVillage directory
        plant_village_path = '../../PlantVillage/PlantVillage'
        test_images = []
        for category in os.listdir(plant_village_path):
            category_path = os.path.join(plant_village_path, category)
            if os.path.isdir(category_path):
                image_files = os.listdir(category_path)
                if image_files:
                    # Get the first image from each category
                    img_path = os.path.join(category_path, image_files[0])
                    test_images.append((img_path, category))
                    if len(test_images) >= 3:  # Test with 3 images
                        break
        
        # Test predictions
        for img_path, true_category in test_images:
            # Load and preprocess image
            img = Image.open(img_path).convert('RGB')
            img = img.resize((224, 224))
            img_array = np.expand_dims(np.array(img) / 255.0, axis=0)
            
            # Make prediction
            prediction = model.predict(img_array)
            predicted_class = max(class_indices.items(), key=lambda x: prediction[0][x[1]])[0]
            confidence = np.max(prediction)
            
            print(f"\nTest image: {os.path.basename(img_path)}")
            print(f"True category: {true_category}")
            print(f"Predicted category: {predicted_class}")
            print(f"Confidence: {confidence:.2%}")
            
        return True
    except Exception as e:
        print(f"Error testing disease detection model: {e}")
        return False

def main():
    print("Starting model testing...")
    
    # Test crop recommendation model
    crop_success = test_crop_recommendation()
    
    # Test disease detection model
    disease_success = test_disease_detection()
    
    # Print overall results
    print("\nTesting Results:")
    print(f"Crop Recommendation Model: {'SUCCESS' if crop_success else 'FAILED'}")
    print(f"Disease Detection Model: {'SUCCESS' if disease_success else 'FAILED'}")

if __name__ == "__main__":
    main()