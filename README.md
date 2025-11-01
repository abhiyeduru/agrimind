# 🌾 AgriMind.AI

AI-Powered Voice & Image Farming Assistant for Every Farmer — Smart Crop, Smart Care.

## Features

✅ AI Chatbot (OpenAI API) – Friendly farming Q&A
✅ Crop Recommendation (ML model)
✅ Disease Detection (Image + TensorFlow)
✅ Firebase Storage (farmer data + chats)
✅ Multi-language Support (English, Telugu, Hindi)
✅ Smart Dashboard (past queries + results)

## Setup Instructions

1. Clone the repository
2. Set up the environment variables:
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your API keys
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```bash
   cd frontend
   pip install -r requirements.txt
   ```

5. Train and save the ML models:
   ```bash
   python train_models.py
   ```

6. Start the backend server:
   ```bash
   cd backend
   uvicorn app:app --reload
   ```

7. Start the Streamlit frontend:
   ```bash
   cd frontend
   streamlit run demo.py
   ```

## ML Models

### Crop Recommendation Model
- Input: N, P, K, temperature, humidity, pH, rainfall
- Output: Best crop suggestion
- Model: RandomForestClassifier

### Disease Detection Model
- Input: Leaf Image
- Output: Disease Label + Confidence
- Model: MobileNetV2 (transfer learning with PlantVillage dataset)

## API Endpoints

- `/recommend_crop` - Get crop recommendations
- `/detect_disease` - Detect plant diseases from images
- `/chat` - Chat with AI farming assistant

## Tech Stack

- Frontend: Streamlit
- Backend: FastAPI
- AI: OpenAI GPT-4, TensorFlow, scikit-learn
- Database: Firebase Firestore
- Languages: Python

## Environment Variables

Required environment variables in `.env`:
- `OPENAI_API_KEY`: Your OpenAI API key
- `FIREBASE_CONFIG`: Path to Firebase config JSON
- `OPENWEATHER_API_KEY`: OpenWeather API key for weather data

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions and support, please open an issue in the GitHub repository.