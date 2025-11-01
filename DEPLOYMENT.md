# 🚀 AgriMindAI Deployment Guide

## Quick Deploy Options

### Option 1: Render (Recommended - Easiest) ⭐

#### Prerequisites:
- GitHub account with your code pushed
- Render account (sign up at render.com)

#### Steps:

**Deploy Backend:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `abhiyeduru/agrimind`
4. Configure:
   - **Name**: `agrimind-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"
6. **Important**: Copy the backend URL (e.g., `https://agrimind-backend.onrender.com`)

**Deploy Frontend:**
1. Click "New +" → "Web Service" again
2. Select same repository
3. Configure:
   - **Name**: `agrimind-frontend`
   - **Root Directory**: `frontend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run Home.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
4. Add Environment Variable:
   - **Key**: `BACKEND_URL`
   - **Value**: Your backend URL from step 1
5. Click "Create Web Service"

**⚠️ Important Note:**
- Free tier services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Consider upgrading to paid tier for production use

---

### Option 2: Streamlit Cloud (Frontend Only)

#### Steps:
1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Sign in with GitHub
3. Click "New app"
4. Select:
   - **Repository**: `abhiyeduru/agrimind`
   - **Branch**: `main`
   - **Main file path**: `frontend/Home.py`
5. Click "Deploy"

**For Backend:** Deploy to Render or Railway separately

---

### Option 3: Railway

#### Steps:
1. Go to [Railway](https://railway.app/)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect and deploy both services

---

### Option 4: Heroku

#### Prerequisites:
```bash
# Install Heroku CLI
brew install heroku/brew/heroku
```

#### Deploy Backend:
```bash
cd backend
heroku login
heroku create agrimind-backend
git push heroku main
```

#### Deploy Frontend:
```bash
cd frontend
heroku create agrimind-frontend
git push heroku main
```

---

## ⚙️ Configuration Files Included

- `render.yaml` - Render deployment config
- `Procfile` - Heroku/Railway process file
- `runtime.txt` - Python version specification

---

## 🔧 Environment Variables Needed

### Backend:
- `OPENAI_API_KEY` (for chat feature)
- `FIREBASE_CONFIG` (Firebase credentials - use secrets manager)

### Frontend:
- `BACKEND_URL` (URL of your deployed backend)

---

## 📦 Before Deployment

### 1. Train Models Locally
```bash
cd backend
python train_models.py
```
This creates:
- `models/crop_rf.joblib`
- `models/disease_mobilenet.h5`
- `models/disease_classes.joblib`

### 2. Upload Models
Since model files are large (excluded from git), you need to:
- **Option A**: Store in cloud storage (Google Cloud Storage, AWS S3)
- **Option B**: Upload via Render disk or persistent storage
- **Option C**: Train on deployment server (slow but works)

---

## 🐛 Troubleshooting

### "Page Not Found" Error:
- Check if service is running: Visit backend URL + `/docs` for API docs
- Verify `BACKEND_URL` environment variable in frontend
- Check logs in deployment platform dashboard

### Models Not Loading:
- Ensure models are uploaded to deployment server
- Check file paths in `app.py` and `simple_app.py`
- Verify model files exist in `backend/models/` directory

### Import Errors:
- Check all dependencies in `requirements.txt`
- Ensure Python version matches (3.9)
- Check deployment logs for specific errors

---

## 💡 Cost Estimates

### Free Tier:
- **Render**: 750 hours/month free (services sleep when inactive)
- **Streamlit Cloud**: Unlimited for public apps
- **Railway**: $5 free credit/month

### Paid (Recommended for Production):
- **Render**: ~$7/month per service
- **Railway**: Pay-as-you-go, ~$10-20/month
- **Heroku**: ~$7/month per dyno

---

## 📝 Post-Deployment Checklist

- [ ] Backend API is accessible
- [ ] Frontend loads correctly
- [ ] Disease detection works with test images
- [ ] Crop recommendation returns predictions
- [ ] Chat feature connects to OpenAI (if configured)
- [ ] Set up custom domain (optional)
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Set up monitoring/logging
- [ ] Configure auto-scaling (optional)

---

## 🔗 Useful Links

- [Render Documentation](https://render.com/docs)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

---

## Need Help?

If deployment fails:
1. Check deployment logs in platform dashboard
2. Verify all environment variables are set
3. Test backend API using `/docs` endpoint
4. Check GitHub repository has all required files
