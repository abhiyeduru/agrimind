#!/bin/bash

echo "🔥 Firebase Cloud Run Deployment for AgriMindAI"
echo "================================================"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found!"
    echo "Installing..."
    brew install google-cloud-sdk
    export PATH=/opt/homebrew/share/google-cloud-sdk/bin:"$PATH"
fi

# Login to Google Cloud
echo "📝 Step 1: Login to Google Cloud..."
gcloud auth login

# Set project
echo ""
echo "📋 Step 2: Select or create a project..."
echo "Enter your Google Cloud Project ID (or press Enter to create new):"
read PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "Creating new project..."
    PROJECT_ID="agrimind-$(date +%s)"
    gcloud projects create $PROJECT_ID
fi

gcloud config set project $PROJECT_ID

# Enable required APIs
echo ""
echo "🔧 Step 3: Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Set region
REGION="us-central1"
gcloud config set run/region $REGION

# Deploy Backend
echo ""
echo "🚀 Step 4: Deploying Backend..."
cd backend

gcloud run deploy agrimind-backend \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300 \
  --set-env-vars "PYTHON_VERSION=3.9"

# Get backend URL
BACKEND_URL=$(gcloud run services describe agrimind-backend --region=$REGION --format='value(status.url)')
echo ""
echo "✅ Backend deployed at: $BACKEND_URL"

# Deploy Frontend
echo ""
echo "🚀 Step 5: Deploying Frontend..."
cd ../frontend

gcloud run deploy agrimind-frontend \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300 \
  --set-env-vars "BACKEND_URL=$BACKEND_URL,PYTHON_VERSION=3.9"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe agrimind-frontend --region=$REGION --format='value(status.url)')

echo ""
echo "================================================"
echo "✅ Deployment Complete!"
echo "================================================"
echo ""
echo "🌐 Your app is live at:"
echo "   Frontend: $FRONTEND_URL"
echo "   Backend:  $BACKEND_URL"
echo ""
echo "📊 Manage your deployment:"
echo "   https://console.cloud.google.com/run?project=$PROJECT_ID"
echo ""
