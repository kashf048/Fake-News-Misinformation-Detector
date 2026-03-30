# 🧠 Fake News & Misinformation Detector

A production-ready, multimodal AI system that detects fake news and misinformation using advanced machine learning models.

## ✨ Features

### 🤖 AI-Powered Analysis
- **RoBERTa NLP Model**: Advanced text classification for fake news detection
- **CLIP Vision Model**: Image-text similarity analysis
- **Intelligent Decision Engine**: Combines both outputs for accurate predictions

### 📊 Comprehensive Results
- **Prediction**: Fake, Real, or Misleading
- **Confidence Score**: 0-100% accuracy indicator
- **Explanation**: Detailed reasoning for each prediction
- **Image Similarity**: How well image matches headline
- **Fact-Check References**: Integrated Google Fact Check API

### 📈 Analytics Dashboard
- Total analyses count
- Breakdown by prediction type
- Average confidence scores
- Trends over time
- Recent headlines

### 💾 History Management
- View all previous analyses
- Filter by prediction type
- Pagination support
- Delete analyses
- Detailed view with all metadata

### 📄 Report Generation
- PDF reports for individual analyses
- Batch report export
- Professional formatting

---

## 🏗️ Architecture

### Frontend Stack
- **React 19**: Modern UI framework
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first styling
- **TypeScript**: Type-safe development
- **Recharts**: Data visualization
- **Axios**: HTTP client

### Backend Stack
- **FastAPI**: High-performance Python framework
- **MongoDB**: NoSQL database
- **Motor**: Async MongoDB driver
- **Transformers**: Hugging Face models
- **PyTorch**: Deep learning framework

### AI Models
- **RoBERTa-base**: 125M parameters, trained on fake news
- **CLIP ViT-B/32**: Vision-language model
- **Google Fact Check API**: Real-time fact verification

---

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB Atlas account (free tier)
- 5GB+ disk space (for models)

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI and API keys

# Run backend
python main.py
```

Backend runs at: `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Run frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

### 3. Test the Application

1. Open `http://localhost:5173`
2. Enter a headline: "Breaking: Scientists discover cure for disease"
3. Click "Analyze Now"
4. View results with prediction and confidence
5. Explore History and Analytics pages

---

## 📚 Documentation

- [Setup Guide](./SETUP_GUIDE.md) - Detailed installation instructions
- [Run Guide](./RUN_GUIDE.md) - How to run and test the application
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Production deployment steps
- [API Documentation](./API_DOCS.md) - Complete API reference

---

## 🎯 API Endpoints

### Analysis
- `POST /api/analyze` - Analyze headline and image
- `GET /api/history` - Get analysis history
- `DELETE /api/history/{id}` - Delete analysis
- `GET /api/analytics` - Get analytics data
- `GET /api/health` - Health check

See [API Documentation](./API_DOCS.md) for details.

---

## 🧪 Sample Test Data

### Headlines
```
1. "Breaking: Scientists discover cure for disease"
   → Likely Misleading (sensational)

2. "Weather forecast predicts rain tomorrow"
   → Likely Real (factual)

3. "Aliens spotted in downtown area"
   → Likely Fake (extraordinary)
```

### Image URLs
```
https://via.placeholder.com/400x300
https://picsum.photos/400/300
https://images.unsplash.com/photo-1504711331083-9c895941bf81
```

---

## 📊 Project Structure

```
fake-news-detector/
├── backend/
│   ├── app/
│   │   ├── database/        # MongoDB connection
│   │   ├── routes/          # API endpoints
│   │   ├── schemas/         # Pydantic models
│   │   ├── services/        # Business logic
│   │   │   ├── ai_models.py
│   │   │   ├── analysis.py
│   │   │   └── fact_check.py
│   │   └── utils/           # Utilities
│   ├── main.py              # FastAPI app
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── client/
│   │   ├── src/
│   │   │   ├── components/  # React components
│   │   │   ├── pages/       # Page components
│   │   │   ├── services/    # API service
│   │   │   └── App.tsx
│   │   ├── index.html
│   │   └── package.json
│   └── vite.config.js
├── SETUP_GUIDE.md
├── RUN_GUIDE.md
├── DEPLOYMENT_GUIDE.md
└── README.md
```

---

## 🔐 Security

### Environment Variables
```
MONGO_URI=your_mongodb_connection
DB_NAME=misinformation_db
GOOGLE_FACT_CHECK_API_KEY=your_api_key
JWT_SECRET=your_secret_key
ALLOWED_ORIGINS=http://localhost:5173
```

### Best Practices
- Never commit `.env` files
- Use strong JWT secrets
- Enable CORS only for trusted origins
- Validate all inputs
- Use HTTPS in production
- Enable rate limiting

---

## 🚀 Deployment

### Quick Deploy

**Backend** (Render)
```bash
# Push to GitHub
# Connect to Render
# Set environment variables
# Deploy
```

**Frontend** (Vercel)
```bash
# Push to GitHub
# Connect to Vercel
# Set VITE_API_URL
# Deploy
```

See [Deployment Guide](./DEPLOYMENT_GUIDE.md) for detailed steps.

---

## 📈 Performance

### Backend
- Model loading: ~30 seconds (first run)
- Analysis: < 1 second (subsequent)
- Database queries: < 100ms

### Frontend
- Initial load: < 2 seconds
- API response: < 1 second
- UI interactions: < 100ms

---

## 🐛 Troubleshooting

### MongoDB Connection Error
```bash
# Verify connection string
# Check IP whitelist in MongoDB Atlas
# Ensure user has permissions
```

### Model Loading Error
```bash
# Check disk space (5GB+)
# Verify internet connection
# Increase timeout
```

### CORS Error
```bash
# Update ALLOWED_ORIGINS in .env
# Restart backend
```

See [Run Guide](./RUN_GUIDE.md) for more troubleshooting.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) - Transformers library
- [OpenAI](https://openai.com/) - CLIP model
- [Google](https://google.com/) - Fact Check API
- [MongoDB](https://mongodb.com/) - Database
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend framework

---

## 📞 Support

For issues or questions:
1. Check the documentation
2. Review troubleshooting section
3. Check API logs
4. Open an issue on GitHub

---

## 🎯 Roadmap

- [ ] User authentication
- [ ] Advanced analytics
- [ ] Custom model training
- [ ] Real-time notifications
- [ ] Mobile app
- [ ] Browser extension
- [ ] API rate limiting
- [ ] Caching layer

---

## 📊 Stats

- **Models**: 2 (RoBERTa + CLIP)
- **API Endpoints**: 5
- **Components**: 10+
- **Pages**: 3
- **Database Collections**: 1
- **Supported Formats**: Images (JPG, PNG, GIF, WebP)

---

## 🔗 Links

- [GitHub Repository](https://github.com/your-repo)
- [Live Demo](https://fake-news-detector.vercel.app)
- [API Documentation](./API_DOCS.md)
- [Setup Guide](./SETUP_GUIDE.md)

---

**Built with ❤️ for truth and accuracy**

---

## 🎓 Learning Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [React Documentation](https://react.dev/)
- [MongoDB Guide](https://docs.mongodb.com/)
- [Transformers Guide](https://huggingface.co/docs/transformers/)
- [CLIP Paper](https://arxiv.org/abs/2103.14030)

---

**Last Updated**: January 2024
**Version**: 1.0.0
