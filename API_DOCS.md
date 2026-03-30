# API Documentation

## Base URL

```
http://localhost:8000
Production: https://your-backend-url.com
```

---

## Authentication

Currently, the API does not require authentication. In production, implement JWT tokens.

---

## Endpoints

### 1. Analyze Headline

Analyze a headline and optional image for misinformation.

**Endpoint**: `POST /api/analyze`

**Request Body**:
```json
{
  "headline": "Breaking: Scientists discover cure for disease",
  "image_url": "https://example.com/image.jpg"
}
```

**Parameters**:
- `headline` (string, required): News headline or claim (1-1000 chars)
- `image_url` (string, optional): URL to image for analysis

**Response** (200 OK):
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "headline": "Breaking: Scientists discover cure for disease",
  "image_url": "https://example.com/image.jpg",
  "prediction": "Misleading",
  "confidence": 0.85,
  "similarity": 0.42,
  "explanation": "The claim is partially true but lacks scientific evidence...",
  "fact_checks": [
    {
      "title": "Fact Check Source",
      "url": "https://factcheck.org/article",
      "claim_reviewed": "Scientists discover cure",
      "rating": "Mostly False"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Headline is required"
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "detail": "Internal server error"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "Breaking: Scientists discover cure for disease",
    "image_url": "https://example.com/image.jpg"
  }'
```

**Example Python**:
```python
import requests

response = requests.post(
    'http://localhost:8000/api/analyze',
    json={
        'headline': 'Breaking: Scientists discover cure for disease',
        'image_url': 'https://example.com/image.jpg'
    }
)
print(response.json())
```

**Example JavaScript**:
```javascript
const response = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    headline: 'Breaking: Scientists discover cure for disease',
    image_url: 'https://example.com/image.jpg'
  })
});
const data = await response.json();
console.log(data);
```

---

### 2. Get Analysis History

Retrieve analysis history with pagination and filtering.

**Endpoint**: `GET /api/history`

**Query Parameters**:
- `page` (integer, default: 1): Page number for pagination
- `limit` (integer, default: 10, max: 100): Results per page
- `prediction` (string, optional): Filter by prediction type ("Fake", "Real", "Misleading")

**Response** (200 OK):
```json
{
  "total": 100,
  "page": 1,
  "limit": 10,
  "items": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "headline": "Breaking: Scientists discover cure for disease",
      "image_url": "https://example.com/image.jpg",
      "prediction": "Misleading",
      "confidence": 0.85,
      "similarity": 0.42,
      "explanation": "...",
      "fact_checks": [],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Example cURL**:
```bash
# Get first page
curl http://localhost:8000/api/history

# Get page 2 with 20 items per page
curl http://localhost:8000/api/history?page=2&limit=20

# Filter by prediction type
curl http://localhost:8000/api/history?prediction=Fake
```

**Example JavaScript**:
```javascript
// Get history
const response = await fetch('http://localhost:8000/api/history?page=1&limit=10');
const data = await response.json();
console.log(data.items);

// Filter by prediction
const fakeResponse = await fetch('http://localhost:8000/api/history?prediction=Fake');
const fakeData = await fakeResponse.json();
```

---

### 3. Delete Analysis

Delete a specific analysis by ID.

**Endpoint**: `DELETE /api/history/{id}`

**Path Parameters**:
- `id` (string, required): Analysis ID (MongoDB ObjectId)

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Analysis deleted successfully"
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Analysis not found"
}
```

**Example cURL**:
```bash
curl -X DELETE http://localhost:8000/api/history/507f1f77bcf86cd799439011
```

**Example JavaScript**:
```javascript
const response = await fetch('http://localhost:8000/api/history/507f1f77bcf86cd799439011', {
  method: 'DELETE'
});
const data = await response.json();
console.log(data.message);
```

---

### 4. Get Analytics

Retrieve analytics and statistics data.

**Endpoint**: `GET /api/analytics`

**Response** (200 OK):
```json
{
  "total_analyses": 100,
  "fake_count": 30,
  "real_count": 50,
  "misleading_count": 20,
  "average_confidence": 0.85,
  "predictions_by_date": {
    "2024-01-15": 10,
    "2024-01-16": 15,
    "2024-01-17": 12
  },
  "top_headlines": [
    "Breaking: Scientists discover cure for disease",
    "Weather forecast predicts rain tomorrow",
    "Stock market rises 2% in trading"
  ]
}
```

**Example cURL**:
```bash
curl http://localhost:8000/api/analytics
```

**Example JavaScript**:
```javascript
const response = await fetch('http://localhost:8000/api/analytics');
const data = await response.json();
console.log(`Total: ${data.total_analyses}`);
console.log(`Fake: ${data.fake_count}`);
console.log(`Real: ${data.real_count}`);
console.log(`Misleading: ${data.misleading_count}`);
```

---

### 5. Health Check

Check API health status.

**Endpoint**: `GET /api/health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "Fake News Detector API",
  "version": "1.0.0"
}
```

**Example cURL**:
```bash
curl http://localhost:8000/api/health
```

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

---

## Data Types

### Prediction
```
"Fake" | "Real" | "Misleading"
```

### Confidence Score
```
0.0 - 1.0 (0% - 100%)
```

### Similarity Score
```
0.0 - 1.0 (0% - 100%)
```

### Timestamp
```
ISO 8601 format: "2024-01-15T10:30:00Z"
```

---

## Error Handling

### Common Errors

**Missing Required Field**:
```json
{
  "detail": [
    {
      "loc": ["body", "headline"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Invalid Field Type**:
```json
{
  "detail": [
    {
      "loc": ["body", "confidence"],
      "msg": "value is not a valid float",
      "type": "type_error.float"
    }
  ]
}
```

**Server Error**:
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting. In production:
- Limit: 100 requests per minute per IP
- Burst: 10 requests per second

---

## CORS

Allowed origins (configurable):
```
http://localhost:5173
http://localhost:3000
https://your-frontend.vercel.app
```

---

## Pagination

All list endpoints support pagination:

```
GET /api/history?page=1&limit=10
```

- `page`: 1-indexed page number
- `limit`: 1-100 items per page (default: 10)

**Response includes**:
- `total`: Total number of items
- `page`: Current page
- `limit`: Items per page
- `items`: Array of items

---

## Filtering

### By Prediction Type

```
GET /api/history?prediction=Fake
GET /api/history?prediction=Real
GET /api/history?prediction=Misleading
```

---

## Sorting

Results are sorted by `created_at` in descending order (newest first).

---

## Example Workflows

### Complete Analysis Flow

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Analyze headline
response = requests.post(f"{BASE_URL}/api/analyze", json={
    "headline": "Breaking news headline",
    "image_url": "https://example.com/image.jpg"
})
result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}")

# 2. Get history
history_response = requests.get(f"{BASE_URL}/api/history")
history = history_response.json()
print(f"Total analyses: {history['total']}")

# 3. Get analytics
analytics_response = requests.get(f"{BASE_URL}/api/analytics")
analytics = analytics_response.json()
print(f"Average confidence: {analytics['average_confidence']}")

# 4. Delete analysis
delete_response = requests.delete(f"{BASE_URL}/api/history/{result['_id']}")
print(delete_response.json()['message'])
```

### Filter and Paginate

```javascript
// Get fake news only, page 2
const response = await fetch(
  'http://localhost:8000/api/history?prediction=Fake&page=2&limit=20'
);
const data = await response.json();
console.log(`Showing ${data.items.length} of ${data.total} fake news`);
```

---

## WebSocket (Future)

Real-time analysis updates (planned):
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analysis');
ws.onmessage = (event) => {
  console.log('Analysis update:', event.data);
};
```

---

## Batch Operations (Future)

Analyze multiple headlines:
```bash
POST /api/analyze/batch
```

---

## Export (Future)

Export analyses as CSV/PDF:
```bash
GET /api/history/export?format=csv
GET /api/history/export?format=pdf
```

---

## Versioning

Current API version: `1.0.0`

Future versions will use:
```
/api/v1/analyze
/api/v2/analyze
```

---

## Documentation

- Interactive API docs: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI schema: `http://localhost:8000/api/openapi.json`

---

## Support

For API issues:
1. Check this documentation
2. Review error messages
3. Check server logs
4. Verify environment variables
5. Contact support

---

**Last Updated**: January 2024
**Version**: 1.0.0
