# Fake News & Misinformation Detector - Run Guide

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB Atlas account with connection string
- Google Fact Check API key (optional)

### 1. Backend Setup & Run

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file with your MongoDB URI
cat > .env << EOF
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=misinformation_db
MODEL_NAME=roberta-base
CLIP_MODEL=openai/clip-vit-base-patch32
GOOGLE_FACT_CHECK_API_KEY=your_api_key
API_PORT=8000
API_HOST=0.0.0.0
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
JWT_SECRET=your-secret-key
ALGORITHM=HS256
EOF

# Run the backend
python main.py
```

Backend will be available at: `http://localhost:8000`

### 2. Frontend Setup & Run

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
# or
pnpm dev
```

Frontend will be available at: `http://localhost:5173`

## 📊 Testing the Application

### Test Backend API

```bash
# 1. Health check
curl http://localhost:8000/api/health

# 2. Analyze a headline
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "Breaking: Scientists discover cure for disease",
    "image_url": "https://example.com/image.jpg"
  }'

# 3. Get analysis history
curl http://localhost:8000/api/history

# 4. Get analytics
curl http://localhost:8000/api/analytics

# 5. Delete an analysis (replace ID)
curl -X DELETE http://localhost:8000/api/history/507f1f77bcf86cd799439011
```

### Test Frontend UI

1. Open `http://localhost:5173` in your browser
2. You should see the Fake News Detector home page
3. Test the following features:

#### Analyze Feature
- Enter a headline: "Breaking: Scientists discover cure for disease"
- Optionally add an image URL
- Click "Analyze Now"
- View the results with prediction, confidence, and explanation

#### History Feature
- Click "History" in the navigation
- View all previous analyses
- Filter by prediction type (Fake, Real, Misleading)
- Click on any analysis to view details
- Delete analyses with the trash button

#### Analytics Feature
- Click "Analytics" in the navigation
- View statistics dashboard with:
  - Total analyses count
  - Breakdown by prediction type
  - Confidence averages
  - Prediction trends over time
  - Recent headlines

## 🔍 Sample Test Data

### Test Headlines

```
1. "Breaking: Scientists discover cure for disease"
   Expected: Likely Misleading (sensational claim)

2. "Weather forecast predicts rain tomorrow"
   Expected: Likely Real (factual statement)

3. "Aliens spotted in downtown area"
   Expected: Likely Fake (extraordinary claim)

4. "Stock market rises 2% in trading"
   Expected: Likely Real (factual data)

5. "Celebrity announces retirement from industry"
   Expected: Depends on context (could be any)
```

### Test Image URLs

```
https://via.placeholder.com/400x300?text=News+Image
https://picsum.photos/400/300
https://images.unsplash.com/photo-1504711331083-9c895941bf81
```

## 🛠️ Development Commands

### Backend

```bash
# Run with auto-reload
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests (if available)
pytest

# Format code
black app/ main.py

# Lint code
flake8 app/ main.py
```

### Frontend

```bash
# Development with HMR
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run check

# Format code
npm run format
```

## 📈 Performance Tips

### Backend Optimization
- Models are loaded once on startup (takes ~30 seconds first run)
- Subsequent requests are fast (< 1 second)
- Use connection pooling for MongoDB
- Consider caching frequent queries

### Frontend Optimization
- React components are code-split automatically
- Tailwind CSS is purged in production
- Images are lazy-loaded
- API calls use axios with timeout

## 🔐 Security Checklist

Before production deployment:

- [ ] Change `JWT_SECRET` to a strong random string
- [ ] Set `ALLOWED_ORIGINS` to your production domain
- [ ] Enable MongoDB Atlas IP whitelist
- [ ] Use HTTPS for all connections
- [ ] Set up rate limiting
- [ ] Validate and sanitize all inputs
- [ ] Use environment variables for secrets
- [ ] Enable CORS only for trusted origins
- [ ] Set up logging and monitoring
- [ ] Regular security updates for dependencies

## 🚨 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'transformers'"
**Solution:**
```bash
pip install --upgrade transformers torch
```

### Issue: "CORS error when calling API"
**Solution:**
```bash
# Check ALLOWED_ORIGINS in backend .env
# Should include your frontend URL
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Issue: "MongoDB connection timeout"
**Solution:**
```bash
# Verify connection string
# Check IP whitelist in MongoDB Atlas
# Ensure database user has correct permissions
```

### Issue: "Models taking too long to load"
**Solution:**
```bash
# First run downloads models (~2GB)
# Subsequent runs use cached models
# Check disk space: at least 5GB required
```

### Issue: "Frontend shows blank page"
**Solution:**
```bash
# Check browser console for errors
# Verify VITE_API_URL is correct
# Ensure backend is running
# Clear browser cache and reload
```

## 📊 Monitoring

### Backend Logs
```bash
# Check recent logs
tail -f backend/logs/app.log

# Search for errors
grep ERROR backend/logs/app.log
```

### Frontend Logs
```bash
# Open browser DevTools (F12)
# Check Console tab for errors
# Check Network tab for API calls
```

## 🔄 Restart Services

### Restart Backend
```bash
# Stop current process (Ctrl+C)
# Reactivate virtual environment
source venv/bin/activate
# Run again
python main.py
```

### Restart Frontend
```bash
# Stop current process (Ctrl+C)
# Run again
npm run dev
```

## 📝 Database Maintenance

### Backup Data
```bash
# MongoDB Atlas provides automatic backups
# Manual export:
mongoexport --uri "mongodb+srv://..." --collection analyses --out analyses.json
```

### Clear Old Data
```bash
# Via API (if implemented)
# Or manually in MongoDB Atlas dashboard
```

## 🎯 Next Steps

1. **Customize Models**: Replace RoBERTa/CLIP with your trained models
2. **Add Authentication**: Implement user accounts
3. **Deploy**: Use Render, Vercel, or your preferred platform
4. **Monitor**: Set up error tracking (Sentry, LogRocket)
5. **Scale**: Add caching, CDN, load balancing

## 📚 Documentation

- [API Documentation](./API_DOCS.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Component Guide](./COMPONENT_GUIDE.md)

## 💡 Tips

- Use `curl` or Postman to test API endpoints
- Enable browser DevTools for frontend debugging
- Check logs for detailed error messages
- Start with test data before using real headlines
- Monitor API response times in production

## 📞 Support

For issues:
1. Check this guide's troubleshooting section
2. Review API logs
3. Check browser console
4. Verify environment variables
5. Ensure all services are running

---

**Happy analyzing! 🚀**
