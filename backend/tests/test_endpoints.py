import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from main import app

client = TestClient(app)


@pytest.fixture
def mock_services():
    """Mock the external service dependencies of the analyze endpoint"""
    with patch("app.routes.analysis.run_in_threadpool") as mock_threadpool, \
         patch("app.routes.analysis.FactCheckService.search_fact_checks", new_callable=AsyncMock) as mock_fact_check, \
         patch("app.routes.analysis.AnalysisService.save_analysis", new_callable=AsyncMock) as mock_save, \
         patch("app.routes.analysis.AnalysisService.get_analysis", new_callable=AsyncMock) as mock_get:
        
        # Mock text analysis returning (prediction, confidence)
        mock_threadpool.side_effect = lambda func, *args, **kwargs: (
            ("Fake", 0.95) if func.__name__ == "analyze_text" else
            (0.85 if func.__name__ == "analyze_image_text_similarity" else True)
        )
        
        mock_fact_check.return_value = []
        mock_save.return_value = "mocked_id_123"
        mock_get.return_value = {
            "headline": "A valid news headline text",
            "image_url": "https://example.com/image.jpg",
            "prediction": "Fake",
            "confidence": 0.95,
            "similarity": 0.85,
            "explanation": "Mocked explanation",
            "fact_checks": [],
            "created_at": "2026-07-18T10:00:00Z"
        }
        
        yield {
            "threadpool": mock_threadpool,
            "fact_check": mock_fact_check,
            "save": mock_save,
            "get": mock_get
        }


def test_health_endpoint():
    """Test health endpoint returns 200 and healthy status"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint returns welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]


def test_analyze_empty_headline():
    """Test analyze endpoint with empty headline returns 422"""
    response = client.post("/api/analyze", json={"headline": "", "image_url": None})
    assert response.status_code == 422
    assert "string_too_short" in response.text or "less than" in response.text


def test_analyze_too_short_headline():
    """Test analyze endpoint with too short headline returns 400"""
    response = client.post("/api/analyze", json={"headline": "ab", "image_url": None})
    assert response.status_code == 400
    assert "Headline must be at least" in response.json()["detail"]


def test_analyze_invalid_image_url():
    """Test analyze endpoint with invalid image URL returns 400"""
    response = client.post(
        "/api/analyze",
        json={"headline": "A valid news headline text", "image_url": "invalid-url"}
    )
    assert response.status_code == 400
    assert "Invalid image URL format" in response.json()["detail"]


def test_analyze_success(mock_services):
    """Test analyze endpoint with valid payload returns 200 and success response"""
    response = client.post(
        "/api/analyze",
        json={"headline": "A valid news headline text", "image_url": "https://example.com/image.jpg"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["_id"] == "mocked_id_123"
    assert json_data["prediction"] == "Fake"
    assert json_data["confidence"] == 0.95


def test_history_invalid_prediction():
    """Test history endpoint with invalid prediction query parameter returns 422 validation error"""
    response = client.get("/api/history?prediction=InvalidPredictionType")
    assert response.status_code == 422


@patch("app.routes.analysis.AnalysisService.get_history", new_callable=AsyncMock)
def test_history_success(mock_get_history):
    """Test history endpoint returns mock items and pagination data"""
    mock_get_history.return_value = {
        "total": 1,
        "page": 1,
        "limit": 10,
        "items": [{
            "_id": "mock_id_999",
            "headline": "Historic headline",
            "image_url": "https://example.com/img.png",
            "prediction": "Real",
            "confidence": 0.99,
            "similarity": 0.9,
            "explanation": "History test",
            "fact_checks": [],
            "created_at": "2026-07-18T10:00:00Z"
        }]
    }
    
    response = client.get("/api/history?page=1&limit=10&prediction=Real")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["prediction"] == "Real"
