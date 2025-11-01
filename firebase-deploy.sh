#!/bin/bash

echo "🔥 Firebase Deployment Setup"
echo "=============================="
echo ""
echo "⚠️  WARNING: Firebase is not recommended for this Python app!"
echo "Consider using Render or Streamlit Cloud instead."
echo ""

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "Installing Firebase CLI..."
    npm install -g firebase-tools
fi

# Initialize Firebase
echo "Initializing Firebase..."
firebase login
firebase init hosting

# Create Dockerfile for Cloud Run
cat > Dockerfile.backend << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

cat > Dockerfile.frontend << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ .

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF

echo ""
echo "✅ Firebase setup files created!"
echo ""
echo "Next steps:"
echo "1. Deploy backend: gcloud run deploy agrimind-backend --source backend/"
echo "2. Deploy frontend: gcloud run deploy agrimind-frontend --source frontend/"
echo ""
echo "💡 Still recommend using Render instead - it's much easier!"
