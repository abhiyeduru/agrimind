# 🔥 Firebase Cloud Run Deployment Guide

## ⚠️ Important: Cost Warning

**Firebase Cloud Run is NOT entirely free!** You get:
- ✅ 2 million requests/month free
- ✅ 360,000 GB-seconds of memory free
- ⚠️ After that, you pay per use
- ⚠️ **Requires credit card** even for free tier

**Recommendation:** Use **Render** instead - it's truly free with no credit card required!

---

## 🚀 Quick Deploy to Firebase

### **Step 1: Prerequisites**

1. **Google Cloud Account** - Create at https://console.cloud.google.com
2. **Credit Card** - Required for verification (won't be charged on free tier)
3. **Billing Enabled** - Must enable billing in Google Cloud Console

### **Step 2: Run Deployment Script**

```bash
cd "/Users/yeduruabhiram/Desktop/nxtwave buildthon/AgriMindAI"
./deploy-firebase.sh
```

The script will:
1. ✅ Login to Google Cloud
2. ✅ Create/select a project
3. ✅ Enable required APIs
4. ✅ Deploy backend to Cloud Run
5. ✅ Deploy frontend to Cloud Run
6. ✅ Give you the URLs

### **Step 3: Follow Prompts**

The script will ask you to:
- Login with your Google account (browser will open)
- Select or create a project
- Confirm deployments

**Total time: ~10-15 minutes**

---

## 📋 Manual Deployment (Alternative)

If you prefer to deploy manually:

### **Backend:**
```bash
cd backend
gcloud run deploy agrimind-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### **Frontend:**
```bash
cd frontend
gcloud run deploy agrimind-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "BACKEND_URL=<your-backend-url>"
```

---

## ❌ Common Issues

### Issue: "Billing not enabled"
**Fix:** Go to https://console.cloud.google.com/billing and enable billing

### Issue: "APIs not enabled"
**Fix:** Run:
```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com
```

### Issue: "Permission denied"
**Fix:** Run:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## 💰 Cost Estimate

For a small app with ~1000 requests/day:
- **Free tier:** $0/month (well within limits)
- **Beyond free tier:** ~$5-10/month

**Compare with alternatives:**
- **Render:** Free (no credit card)
- **Streamlit Cloud:** Free (no credit card)
- **Railway:** $5 credit/month free

---

## 🎯 Recommendation

**For beginners:** Use **Render** instead!
- ✅ No credit card required
- ✅ Simpler setup
- ✅ Truly free forever
- ✅ Auto-deploy from GitHub

**Firebase is better for:**
- Large-scale production apps
- Need Google Cloud integration
- Advanced features (Cloud SQL, etc.)

---

## 🔗 Useful Links

- Google Cloud Console: https://console.cloud.google.com
- Cloud Run Documentation: https://cloud.google.com/run/docs
- Pricing Calculator: https://cloud.google.com/products/calculator

---

## ⚡ Quick Start (If you still want Firebase)

Just run:
```bash
./deploy-firebase.sh
```

And follow the prompts!

