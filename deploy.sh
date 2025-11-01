#!/bin/bash

echo "🌾 AgriMindAI - Quick Deployment Setup"
echo "======================================"
echo ""

# Check if models exist
if [ ! -f "backend/models/crop_rf.joblib" ] || [ ! -f "backend/models/disease_mobilenet.h5" ]; then
    echo "⚠️  WARNING: Model files not found!"
    echo "You need to train models before deployment."
    echo ""
    read -p "Do you want to train models now? (y/n): " train_choice
    
    if [ "$train_choice" = "y" ]; then
        echo "Training models..."
        cd backend
        source venv_py39/bin/activate
        python train_models.py
        cd ..
        echo "✅ Models trained successfully!"
    else
        echo "⚠️  Remember to train models before deploying!"
    fi
fi

echo ""
echo "📋 Deployment Options:"
echo "1. Render (Recommended - Free tier available)"
echo "2. Streamlit Cloud (Frontend only)"
echo "3. Railway (Full stack)"
echo "4. Heroku (Full stack)"
echo ""

read -p "Choose deployment platform (1-4): " platform

case $platform in
    1)
        echo ""
        echo "🚀 Deploying to Render..."
        echo ""
        echo "Follow these steps:"
        echo "1. Go to https://dashboard.render.com/"
        echo "2. Click 'New +' → 'Web Service'"
        echo "3. Connect GitHub repo: abhiyeduru/agrimind"
        echo "4. Use the configuration from DEPLOYMENT.md"
        echo ""
        echo "Opening deployment guide..."
        open "https://dashboard.render.com/"
        ;;
    2)
        echo ""
        echo "🚀 Deploying to Streamlit Cloud..."
        echo ""
        echo "Follow these steps:"
        echo "1. Go to https://share.streamlit.io/"
        echo "2. Sign in with GitHub"
        echo "3. Deploy: abhiyeduru/agrimind → frontend/Home.py"
        echo ""
        open "https://share.streamlit.io/"
        ;;
    3)
        echo ""
        echo "🚀 Deploying to Railway..."
        echo ""
        echo "Follow these steps:"
        echo "1. Go to https://railway.app/"
        echo "2. New Project → Deploy from GitHub"
        echo "3. Select: abhiyeduru/agrimind"
        echo ""
        open "https://railway.app/"
        ;;
    4)
        echo ""
        echo "🚀 Deploying to Heroku..."
        echo ""
        if ! command -v heroku &> /dev/null; then
            echo "Installing Heroku CLI..."
            brew install heroku/brew/heroku
        fi
        echo "Run these commands:"
        echo "  cd backend"
        echo "  heroku login"
        echo "  heroku create agrimind-backend"
        echo "  git push heroku main"
        ;;
    *)
        echo "Invalid option!"
        ;;
esac

echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo "🔗 GitHub repo: https://github.com/abhiyeduru/agrimind"
