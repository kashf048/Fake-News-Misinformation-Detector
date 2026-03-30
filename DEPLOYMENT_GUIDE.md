# Fake News & Misinformation Detector - Deployment Guide

## 🚀 Deployment Overview

This guide covers deploying the Fake News Detector to production across multiple platforms.

### Architecture
```
Frontend (Vercel) → Backend (Render/Railway) → Database (MongoDB Atlas)
```

---

## 📦 Backend Deployment

### Option 1: Render.com

#### Prerequisites
- Render account
- GitHub repository with backend code

#### Steps

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Create Render Service**
   - Go to [render.com](https://render.com)
   - Click "New +"
   - Select "Web Service"
   - Connect GitHub repository
   - Select backend directory

3. **Configure Service**
   - Name: `fake-news-detector-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**
   - Click "Environment"
   - Add all variables from `.env`:
     ```
     MONGO_URI=mongodb+srv://...
     DB_NAME=misinformation_db
     MODEL_NAME=roberta-base
     CLIP_MODEL=openai/clip-vit-base-patch32
     GOOGLE_FACT_CHECK_API_KEY=your_key
     API_PORT=8000
     FRONTEND_URL=https://your-frontend.vercel.app
     ALLOWED_ORIGINS=https://your-frontend.vercel.app
     JWT_SECRET=your-secret-key
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Get your API URL: `https://fake-news-detector-api.onrender.com`

### Option 2: Railway.app

#### Steps

1. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub"
   - Connect your repository

2. **Configure**
   - Select backend directory
   - Add environment variables
   - Set Python version to 3.11

3. **Deploy**
   - Railway automatically deploys on push
   - Get your API URL from project settings

### Option 3: Hugging Face Spaces

#### Steps

1. **Create Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Select "Docker" as SDK
   - Create Space

2. **Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

3. **Push Code**
```bash
git clone https://huggingface.co/spaces/your-username/fake-news-detector
cd fake-news-detector
# Copy your code
git add .
git commit -m "Deploy"
git push
```

---

## 🎨 Frontend Deployment

### Vercel

#### Prerequisites
- Vercel account
- GitHub repository with frontend code

#### Steps

1. **Push Frontend to GitHub**
```bash
cd frontend
git add .
git commit -m "Frontend code"
git push origin main
```

2. **Import Project to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New..." → "Project"
   - Select your GitHub repository
   - Select frontend directory

3. **Configure Build Settings**
   - Framework: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Set Environment Variables**
   - Add `VITE_API_URL` with your backend URL:
     ```
     VITE_API_URL=https://fake-news-detector-api.onrender.com
     ```

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment (2-3 minutes)
   - Get your frontend URL: `https://fake-news-detector.vercel.app`

### Alternative: Netlify

1. **Connect Repository**
   - Go to [netlify.com](https://netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Select GitHub repository

2. **Configure**
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Add environment variables

3. **Deploy**
   - Netlify automatically deploys on push

---

## 🗄️ Database Setup

### MongoDB Atlas (Already Configured)

1. **Create Cluster**
   - Go to [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
   - Create free cluster
   - Create database user
   - Get connection string

2. **Configure Network Access**
   - Add IP addresses to whitelist
   - For production: add backend server IP

3. **Create Database**
   - Database name: `misinformation_db`
   - Collection: `analyses`

---

## 🔐 Security Configuration

### CORS Setup
```python
# In backend main.py
allowed_origins = [
    "https://your-frontend.vercel.app",
    "https://www.your-domain.com"
]
```

### SSL/TLS
- Vercel: Automatic
- Render: Automatic
- Custom domain: Use Let's Encrypt

### Environment Variables
- Never commit `.env` files
- Use platform's secret management
- Rotate API keys regularly

### Rate Limiting
```python
# Add to backend
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

## 📊 Monitoring & Logging

### Backend Monitoring

**Render**
- Built-in logs dashboard
- Real-time monitoring
- Error tracking

**Railway**
- Deployment logs
- Resource usage
- Error alerts

### Frontend Monitoring

**Vercel**
- Analytics dashboard
- Performance metrics
- Error tracking

### Application Monitoring

**Sentry (Error Tracking)**
```python
# Backend
import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

**LogRocket (Frontend)**
```javascript
// Frontend
import LogRocket from 'logrocket';
LogRocket.init('your-app-id');
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy Backend
        run: |
          # Deploy backend (Render/Railway handles this automatically)
      
      - name: Deploy Frontend
        run: |
          # Deploy frontend (Vercel handles this automatically)
```

---

## 🧪 Pre-Deployment Checklist

- [ ] All environment variables set
- [ ] Database connection tested
- [ ] API endpoints tested
- [ ] Frontend builds successfully
- [ ] CORS configured correctly
- [ ] SSL certificates valid
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Rate limiting enabled
- [ ] Security headers set
- [ ] Database backups enabled
- [ ] Monitoring tools configured

---

## 📈 Performance Optimization

### Backend
```python
# Enable caching
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

# Use connection pooling
from motor.motor_asyncio import AsyncClient
```

### Frontend
```javascript
// Code splitting
const Home = lazy(() => import('./pages/Home'));

// Image optimization
import Image from 'next/image';
```

### Database
```javascript
// Create indexes
db.analyses.createIndex({ created_at: -1 });
db.analyses.createIndex({ prediction: 1 });
```

---

## 🚨 Troubleshooting Deployment

### Backend won't start
```bash
# Check logs
# Verify Python version
# Check dependencies
pip install -r requirements.txt
```

### Frontend shows blank page
```bash
# Check VITE_API_URL
# Verify backend is accessible
# Check browser console
```

### Database connection fails
```bash
# Verify connection string
# Check IP whitelist
# Verify credentials
```

### Models loading error
```bash
# Ensure disk space (5GB+)
# Check internet connection
# Increase timeout
```

---

## 📝 Post-Deployment

### Setup Domain
1. Purchase domain (Namecheap, GoDaddy, etc.)
2. Configure DNS
3. Update CORS origins
4. Update frontend API URL

### Enable HTTPS
- Vercel: Automatic
- Render: Automatic
- Custom: Use Let's Encrypt

### Setup Email Alerts
- Configure error notifications
- Setup uptime monitoring
- Create backup alerts

### Documentation
- Update README with production URLs
- Document API endpoints
- Create runbooks for common issues

---

## 🔄 Continuous Deployment

### Auto-Deploy on Push
```bash
# All platforms support automatic deployment
# Just push to main branch
git push origin main
```

### Rollback
```bash
# Render: Select previous deployment
# Vercel: Select previous deployment
# Railway: Use deployment history
```

---

## 💰 Cost Estimation

| Service | Tier | Cost/Month |
|---------|------|-----------|
| MongoDB Atlas | Free | $0 |
| Render | Starter | $7 |
| Vercel | Free | $0 |
| **Total** | | **$7** |

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Deployment](https://vitejs.dev/guide/ssr.html)

---

## 🎯 Next Steps

1. Deploy backend
2. Deploy frontend
3. Test all features
4. Setup monitoring
5. Configure domain
6. Enable backups
7. Document deployment

---

**Deployment Complete! 🎉**

Your Fake News Detector is now live and ready to use.
