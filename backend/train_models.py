import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
import joblib
from pathlib import Path
import os
from tqdm import tqdm

def train_crop_recommendation_model():
    print("Training crop recommendation model...")
    
    # Load the dataset
    df = pd.read_csv('../../Crop_recommendation.csv')
    print(f"Loaded {len(df)} records from crop recommendation dataset")
    
    # Prepare features and target
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate the model
    accuracy = model.score(X_test, y_test)
    print(f"Crop recommendation model accuracy: {accuracy:.2f}")
    
    # Save the model
    joblib.dump(model, 'models/crop_rf.joblib')
    print("Crop recommendation model saved successfully!")

def train_disease_detection_model():
    print("Training disease detection model...")
    
    # Enable mixed precision training for better performance on Apple Silicon
    try:
        policy = tf.keras.mixed_precision.Policy('mixed_float16')
        tf.keras.mixed_precision.set_global_policy(policy)
        print("Mixed precision training enabled")
    except:
        print("Mixed precision training not supported, continuing with default precision")
    
    # Parameters - reduced for faster training
    IMG_SIZE = 160  # Reduced image size
    BATCH_SIZE = 64  # Increased batch size
    EPOCHS = 5      # Reduced epochs
    
    # Setup data generators with simpler augmentation
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,
        horizontal_flip=True,
        validation_split=0.2
    )
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        '../../PlantVillage/PlantVillage',  # Updated path to match the correct directory structure
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )
    
    validation_generator = train_datagen.flow_from_directory(
        '../../PlantVillage/PlantVillage',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )
    
    # Create a smaller MobileNetV2 model
    base_model = tf.keras.applications.MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        alpha=0.35  # Smaller network
    )
    
    # Freeze the base model
    base_model.trainable = False
    
    # Add simpler custom layers
    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(256, activation='relu')(x)  # Smaller dense layer
    predictions = tf.keras.layers.Dense(len(train_generator.class_indices), activation='softmax')(x)
    
    # Create the final model
    model = tf.keras.models.Model(inputs=base_model.input, outputs=predictions)
    
    # Compile the model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Train the model
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator
    )
    
    # Save the model
    model.save('models/disease_mobilenet.h5')
    print("Disease detection model saved successfully!")
    
    # Save class indices
    class_indices = train_generator.class_indices
    joblib.dump(class_indices, 'models/disease_classes.joblib')
    print("Class indices saved successfully!")

def main():
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Train both models
    train_crop_recommendation_model()
    train_disease_detection_model()

if __name__ == "__main__":
    main()