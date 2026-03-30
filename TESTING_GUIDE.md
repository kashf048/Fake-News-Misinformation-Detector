# Testing Guide - Fake News Detector

## Overview

This guide covers all testing aspects of the Fake News & Misinformation Detector project, including unit tests, integration tests, and end-to-end tests.

---

## Backend Testing

### Unit Tests

#### Authentication Tests

```bash
# Run authentication tests
pytest backend/tests/test_auth.py -v

# Run with coverage
pytest backend/tests/test_auth.py --cov=app.security --cov-report=html
```

**Test Cases**:
- Password hashing and verification
- JWT token creation and verification
- Token expiration handling
- Invalid token handling

#### Validator Tests

```bash
# Run validator tests
pytest backend/tests/test_validators.py -v
```

**Test Cases**:
- Headline validation (length, content)
- Email validation (format)
- Password validation (strength)
- Image URL validation
- File size validation
- XSS protection
- HTML escaping

### Integration Tests

#### API Endpoint Tests

```bash
# Run all integration tests
pytest backend/tests/test_api.py -v

# Run specific test
pytest backend/tests/test_api.py::test_analyze_endpoint -v
```

**Test Cases**:
- POST /api/analyze (with and without image)
- GET /api/history (pagination, filtering)
- DELETE /api/history/{id}
- GET /api/analytics
- GET /api/health

#### Database Tests

```bash
# Run database tests
pytest backend/tests/test_database.py -v
```

**Test Cases**:
- Connection establishment
- CRUD operations
- Query optimization
- Index creation
- Transaction handling

### Running All Tests

```bash
# Run all tests with coverage
pytest backend/tests/ -v --cov=app --cov-report=html

# Run tests with specific markers
pytest backend/tests/ -m "not slow" -v

# Run tests with timeout
pytest backend/tests/ --timeout=300 -v
```

### Test Configuration

**pytest.ini**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

---

## Frontend Testing

### Unit Tests

#### Component Tests

```bash
# Run component tests
npm run test -- --coverage

# Run specific component test
npm run test -- FileUpload.test.tsx

# Run tests in watch mode
npm run test -- --watch
```

**Test Cases**:
- Component rendering
- Props validation
- Event handling
- State management
- Error boundaries

#### Service Tests

```bash
# Run API service tests
npm run test -- api.test.ts
```

**Test Cases**:
- API client initialization
- Request formatting
- Error handling
- Response parsing

### Integration Tests

#### Page Tests

```bash
# Run page integration tests
npm run test -- pages/
```

**Test Cases**:
- Page rendering
- Navigation
- Form submission
- Data display

### E2E Tests

#### Cypress Tests

```bash
# Install Cypress
npm install --save-dev cypress

# Run Cypress tests
npx cypress open

# Run tests headless
npx cypress run
```

**Test Scenarios**:
1. User analyzes headline
2. User views history
3. User filters results
4. User deletes analysis
5. User views analytics

### Test Coverage

```bash
# Generate coverage report
npm run test -- --coverage --coverage-reporters=html

# View coverage report
open coverage/index.html
```

---

## API Testing

### Manual Testing with cURL

#### Analyze Endpoint

```bash
# Basic analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "Breaking: Scientists discover cure for disease",
    "image_url": "https://example.com/image.jpg"
  }'

# Analysis without image
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "Weather forecast predicts rain tomorrow"
  }'
```

#### History Endpoint

```bash
# Get all history
curl http://localhost:8000/api/history

# Get with pagination
curl http://localhost:8000/api/history?page=1&limit=10

# Get with filter
curl http://localhost:8000/api/history?prediction=Fake

# Get with both
curl http://localhost:8000/api/history?page=1&limit=10&prediction=Misleading
```

#### Delete Endpoint

```bash
# Delete analysis (replace ID)
curl -X DELETE http://localhost:8000/api/history/507f1f77bcf86cd799439011
```

#### Analytics Endpoint

```bash
# Get analytics
curl http://localhost:8000/api/analytics
```

### Postman Testing

1. Import API collection
2. Set environment variables
3. Run requests
4. Verify responses
5. Check status codes

**Collection Structure**:
```
Fake News Detector
├── Analysis
│   ├── Analyze Headline
│   ├── Analyze with Image
│   └── Analyze Invalid
├── History
│   ├── Get All
│   ├── Get Paginated
│   ├── Get Filtered
│   └── Delete
├── Analytics
│   └── Get Analytics
└── Health
    ├── Health Check
    └── Status
```

---

## Load Testing

### Using Apache Bench

```bash
# Simple load test
ab -n 100 -c 10 http://localhost:8000/api/health

# POST request load test
ab -n 100 -c 10 -p data.json -T application/json \
  http://localhost:8000/api/analyze
```

### Using Locust

**locustfile.py**
```python
from locust import HttpUser, task, between

class FakeNewsUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def analyze(self):
        self.client.post("/api/analyze", json={
            "headline": "Test headline"
        })

    @task
    def get_history(self):
        self.client.get("/api/history")

    @task
    def get_analytics(self):
        self.client.get("/api/analytics")
```

```bash
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

---

## Performance Testing

### Backend Performance

```bash
# Profile code execution
python -m cProfile -s cumulative main.py

# Memory profiling
pip install memory-profiler
python -m memory_profiler main.py
```

### Frontend Performance

```bash
# Lighthouse audit
npm install -g lighthouse
lighthouse http://localhost:3000 --view

# Bundle analysis
npm run build -- --analyze
```

---

## Security Testing

### Vulnerability Scanning

```bash
# Backend security scan
bandit -r backend/app/

# Dependency check
safety check

# OWASP ZAP
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000/api/docs
```

### Input Validation Testing

```bash
# Test XSS prevention
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "<script>alert(\"xss\")</script>"
  }'

# Test SQL injection (MongoDB)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "headline": "'; db.users.find(); //'"
  }'

# Test file upload
curl -X POST http://localhost:8000/api/upload \
  -F "file=@malicious.exe"
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ --cov
```

---

## Test Data

### Sample Headlines

```javascript
// Real news
"Federal Reserve raises interest rates"
"New vaccine approved by FDA"
"Stock market reaches all-time high"

// Fake news
"Aliens spotted in downtown area"
"Government announces free money program"
"Scientists discover perpetual motion machine"

// Misleading
"Study shows coffee is deadly"
"Local politician caught in scandal"
"New diet cures all diseases"
```

### Sample Images

```
https://via.placeholder.com/400x300?text=News+Image
https://picsum.photos/400/300
https://images.unsplash.com/photo-1504711331083-9c895941bf81
```

---

## Debugging

### Backend Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py

# Use debugger
import pdb; pdb.set_trace()

# View logs
tail -f logs/app.log
```

### Frontend Debugging

```bash
# React DevTools
npm install --save-dev @react-devtools/shell-extension

# Browser DevTools
F12 → Console/Network/Performance

# Debug mode
npm run dev -- --inspect
```

---

## Test Checklist

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code coverage > 80%
- [ ] No security vulnerabilities
- [ ] Load test passes (100 req/s)
- [ ] All API endpoints tested
- [ ] All UI components tested
- [ ] Error handling tested
- [ ] Edge cases tested
- [ ] Performance acceptable

---

**Testing Guide Version**: 1.0.0
**Last Updated**: January 2024
