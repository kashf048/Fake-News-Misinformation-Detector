# Fake News & Misinformation Detector - Setup Guide

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB Atlas account (free tier available)
- Git

## 🔧 Installation Steps

### 1. MongoDB Setup

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account or sign in
3. Create a new project
4. Create a cluster (select free tier)
5. Create a database user with credentials
6. Get your connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`)

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your values
# MONGO_URI=your_mongodb_connection_string
# DB_NAME=misinformation_db
# GOOGLE_FACT_CHECK_API_KEY=your_api_key (optional)
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

### 4. Get API Keys (Optional)

#### Google Fact Check API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Fact Check Tools API
4. Create an API key
5. Add it to your backend `.env` file

## 🚀 Running the Application

### Start Backend

```bash
cd backend

# Activate virtual environment (if not already activated)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run the server
python main.py
```

The backend will start at `http://localhost:8000`

### Start Frontend

```bash
cd frontend

# Development mode
npm run dev
# or
pnpm dev
```

The frontend will start at `http://localhost:5173`

## 📝 Environment Variables

### Backend (.env)

```
# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=misinformation_db

# Model Configuration
MODEL_NAME=roberta-base
CLIP_MODEL=openai/clip-vit-base-patch32

# API Configuration
GOOGLE_FACT_CHECK_API_KEY=your_api_key_here
API_PORT=8000
API_HOST=0.0.0.0

# CORS Configuration
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Security
JWT_SECRET=your-secret-key-change-in-production
ALGORITHM=HS256

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp
```

### Frontend (.env.local)

```
VITE_API_URL=http://localhost:8000
```

## 🧪 Testing the Application

### Test the API

```bash
# Health check
curl http://localhost:8000/api/health

# Analyze a headline
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "Breaking: Scientists discover cure for disease",
    "image_url": "https://example.com/image.jpg"
  }'

# Get history
curl http://localhost:8000/api/history

# Get analytics
curl http://localhost:8000/api/analytics
```

### Test the Frontend

1. Open `http://localhost:5173` in your browser
2. Enter a headline in the text field
3. Optionally upload an image
4. Click "Analyze Now"
5. View the results
6. Navigate to History and Analytics pages

## 📚 API Documentation

### Endpoints

#### POST /api/analyze
Analyze a headline and image

**Request:**
```json
{
  "headline": "string",
  "image_url": "string (optional)"
}
```

**Response:**
```json
{
  "_id": "string",
  "headline": "string",
  "image_url": "string",
  "prediction": "Fake | Real | Misleading",
  "confidence": 0.95,
  "similarity": 0.42,
  "explanation": "string",
  "fact_checks": [
    {
      "title": "string",
      "url": "string",
      "claim_reviewed": "string",
      "rating": "string"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET /api/history
Get analysis history

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 10, max: 100)
- `prediction` (optional: "Fake", "Real", "Misleading")

**Response:**
```json
{
  "total": 100,
  "page": 1,
  "limit": 10,
  "items": [...]
}
```

#### DELETE /api/history/{id}
Delete an analysis

**Response:**
```json
{
  "success": true,
  "message": "Analysis deleted successfully"
}
```

#### GET /api/analytics
Get analytics data

**Response:**
```json
{
  "total_analyses": 100,
  "fake_count": 30,
  "real_count": 50,
  "misleading_count": 20,
  "average_confidence": 0.85,
  "predictions_by_date": {
    "2024-01-15": 10,
    "2024-01-16": 15
  },
  "top_headlines": [...]
}
```

#### GET /api/health
Health check

**Response:**
```json
{
  "status": "healthy",
  "service": "Fake News Detector API",
  "version": "1.0.0"
}
```

## 🐛 Troubleshooting

### MongoDB Connection Error
- Verify your connection string is correct
- Check if your IP is whitelisted in MongoDB Atlas
- Ensure the database user has proper permissions

### Model Loading Error
- First run may take time downloading models
- Ensure you have enough disk space (at least 5GB)
- Check internet connection

### CORS Error
- Verify `ALLOWED_ORIGINS` includes your frontend URL
- Check backend is running on correct port

### API Not Responding
- Check if backend is running: `curl http://localhost:8000/api/health`
- Check logs for errors
- Verify environment variables are set correctly

## 📦 Project Structure

```
fake-news-detector/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   └── connection.py
│   │   ├── models/
│   │   ├── routes/
│   │   │   └── analysis.py
│   │   ├── schemas/
│   │   │   └── analysis.py
│   │   ├── services/
│   │   │   ├── ai_models.py
│   │   │   ├── analysis.py
│   │   │   └── fact_check.py
│   │   ├── utils/
│   │   │   └── pdf_generator.py
│   │   └── __init__.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── client/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── services/
│   │   │   ├── App.tsx
│   │   │   ├── main.tsx
│   │   │   └── index.css
│   │   ├── index.html
│   │   ├── package.json
│   │   └── vite.config.js
│   └── .env.example
└── README.md
```

## 🚀 Deployment

### Backend Deployment (Hugging Face Spaces or Render)

1. Push code to GitHub
2. Connect repository to Hugging Face Spaces or Render
3. Set environment variables
4. Deploy

### Frontend Deployment (Vercel)

1. Push code to GitHub
2. Connect repository to Vercel
3. Set `VITE_API_URL` to your backend URL
4. Deploy

### Database (MongoDB Atlas)

Already hosted - no additional setup needed

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [CLIP Documentation](https://github.com/openai/CLIP)

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check logs for error messages
4. Refer to component documentation

## 📄 License

This project is open source and available under the MIT License.
