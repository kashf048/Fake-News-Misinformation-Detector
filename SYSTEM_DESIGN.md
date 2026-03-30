# System Design - Fake News & Misinformation Detector

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Database Design](#database-design)
6. [API Design](#api-design)
7. [Security Architecture](#security-architecture)
8. [Scalability & Performance](#scalability--performance)
9. [Deployment Architecture](#deployment-architecture)
10. [Error Handling & Resilience](#error-handling--resilience)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React 19 + Vite + Tailwind CSS                         │   │
│  │  - Home Page (Analysis Interface)                       │   │
│  │  - History Page (Results Management)                    │   │
│  │  - Analytics Page (Dashboard)                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI + Uvicorn                                       │   │
│  │  - CORS Middleware                                       │   │
│  │  - Rate Limiting                                         │   │
│  │  - Request Logging                                       │   │
│  │  - Error Handling                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓ 
┌─────────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Services & Models                                       │   │
│  │  - AI Models Service (RoBERTa + CLIP)                   │   │
│  │  - Analysis Service (CRUD)                              │   │
│  │  - Fact Check Service (Google API)                      │   │
│  │  - User Service (Authentication)                        │   │
│  │  - PDF Generator                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Data Access Layer                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  MongoDB + Motor (Async)                                │   │
│  │  - Analyses Collection                                  │   │
│  │  - Users Collection                                     │   │
│  │  - Audit Logs Collection                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Components

### 1. Frontend Components

#### Pages
- **Home.tsx**: Main analysis interface
  - Headline input form
  - Image upload/URL input
  - Analysis results display
  - Error handling

- **History.tsx**: Analysis history management
  - Pagination support
  - Filtering by prediction type
  - Delete functionality
  - Detail view

- **Analytics.tsx**: Analytics dashboard
  - Statistics cards
  - Pie chart (distribution)
  - Bar chart (trends)
  - Recent headlines list

#### Components
- **Navbar**: Navigation and branding
- **Footer**: Footer information
- **FileUpload**: Image upload handler
- **TextInput**: Headline input field
- **Loader**: Loading indicator
- **ConfidenceBar**: Confidence visualization
- **ResultCard**: Result display
- **HistoryCard**: History item card
- **ErrorAlert**: Error message display

#### Services
- **api.ts**: Axios-based API client with error handling

### 2. Backend Services

#### Core Services

**AIModels Service** (`app/services/ai_models.py`)
- RoBERTa text classification
- CLIP image-text similarity
- Explanation generation
- Text analysis and keyword extraction

**Analysis Service** (`app/services/analysis.py`)
- Create analysis record
- Retrieve analysis history
- Delete analysis
- Generate analytics data
- Pagination and filtering

**Fact Check Service** (`app/services/fact_check.py`)
- Google Fact Check API integration
- Fact verification
- Summary generation

**User Service** (`app/services/user.py`)
- User registration
- User authentication
- Password management
- User profile management

#### Security Services

**Authentication** (`app/security/auth.py`)
- JWT token generation
- Password hashing (bcrypt)
- Token verification
- Token refresh

**Dependencies** (`app/security/dependencies.py`)
- Current user extraction
- Authorization checks
- Role-based access control

#### Middleware

**Rate Limiting** (`app/middleware/rate_limit.py`)
- Request throttling
- Per-client rate limiting
- Rate limit headers

**Logging** (`app/utils/logging_config.py`)
- Structured logging
- JSON format output
- Request/response logging

**Validation** (`app/utils/validators.py`)
- Input validation
- XSS protection
- SQL injection prevention
- File validation

### 3. Database Schema

#### Collections

**analyses**
```javascript
{
  _id: ObjectId,
  headline: String,
  image_url: String (optional),
  prediction: String (Fake|Real|Misleading),
  confidence: Float (0-1),
  similarity: Float (0-1, optional),
  explanation: String,
  fact_checks: Array[{
    title: String,
    url: String,
    claim_reviewed: String,
    rating: String
  }],
  user_id: ObjectId (optional),
  created_at: DateTime,
  updated_at: DateTime
}
```

**users**
```javascript
{
  _id: ObjectId,
  email: String (unique),
  password: String (hashed),
  full_name: String,
  role: String (user|admin),
  is_active: Boolean,
  created_at: DateTime,
  updated_at: DateTime,
  last_login: DateTime (optional),
  preferences: {
    notifications_enabled: Boolean,
    email_notifications: Boolean
  }
}
```

**audit_logs**
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  action: String,
  resource: String,
  resource_id: String,
  changes: Object,
  ip_address: String,
  user_agent: String,
  created_at: DateTime
}
```

---

## Data Flow

### Analysis Flow

```
User Input (Headline + Image)
    ↓
Frontend Validation
    ↓
API Request (POST /api/analyze)
    ↓
Backend Input Validation & Sanitization
    ↓
Text Analysis (RoBERTa)
    ├─ Tokenization
    ├─ Inference
    └─ Prediction + Confidence
    ↓
Image Analysis (CLIP) [if image provided]
    ├─ Image Download
    ├─ Image Validation
    ├─ Embedding Generation
    └─ Similarity Score
    ↓
Fact Check Integration (Google API)
    ├─ Search for fact checks
    └─ Aggregate results
    ↓
Explanation Generation
    ├─ Analyze prediction
    ├─ Generate reasoning
    └─ Format explanation
    ↓
Database Storage
    ├─ Save analysis record
    └─ Create audit log
    ↓
Response to Frontend
    ↓
Display Results
```

### History Retrieval Flow

```
User Requests History
    ↓
Frontend Request (GET /api/history?page=1&limit=10)
    ↓
Backend Validation
    ├─ Validate pagination
    └─ Validate filter
    ↓
Database Query
    ├─ Count total records
    ├─ Fetch paginated results
    └─ Apply filters
    ↓
Format Response
    ├─ Convert ObjectIds to strings
    └─ Include metadata
    ↓
Return to Frontend
    ↓
Display History
```

---

## Technology Stack

### Frontend
| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | React | 19.2.1 |
| Build Tool | Vite | 7.1.7 |
| Styling | Tailwind CSS | 4.1.14 |
| Language | TypeScript | 5.6.3 |
| HTTP Client | Axios | 1.12.0 |
| Charts | Recharts | 2.15.2 |
| UI Components | shadcn/ui | Latest |
| Routing | Wouter | 3.3.5 |
| Notifications | Sonner | 2.0.7 |

### Backend
| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | FastAPI | Latest |
| Server | Uvicorn | Latest |
| Language | Python | 3.11 |
| Database | MongoDB | 7.0 |
| Async Driver | Motor | Latest |
| NLP Model | RoBERTa | base |
| Vision Model | CLIP | ViT-B/32 |
| ML Framework | PyTorch | Latest |
| Transformers | Hugging Face | Latest |
| Password Hashing | bcrypt | Latest |
| JWT | PyJWT | Latest |
| Validation | Pydantic | Latest |
| PDF Generation | ReportLab | Latest |

### DevOps & Deployment
| Tool | Purpose |
|------|---------|
| Docker | Containerization |
| Docker Compose | Local orchestration |
| GitHub Actions | CI/CD |
| Render/Railway | Backend hosting |
| Vercel | Frontend hosting |
| MongoDB Atlas | Database hosting |

---

## API Design

### RESTful Endpoints

#### Analysis Endpoints
```
POST /api/analyze
  Request: { headline: string, image_url?: string }
  Response: { _id, headline, prediction, confidence, ... }
  Status: 200, 400, 500

GET /api/history?page=1&limit=10&prediction=Fake
  Response: { total, page, limit, items: [...] }
  Status: 200, 400, 500

DELETE /api/history/{id}
  Response: { success: true, message: string }
  Status: 200, 404, 500

GET /api/analytics
  Response: { total_analyses, fake_count, real_count, ... }
  Status: 200, 500
```

#### Authentication Endpoints
```
POST /api/auth/register
  Request: { email, password, full_name }
  Response: { access_token, refresh_token, expires_in }
  Status: 201, 400, 409, 500

POST /api/auth/login
  Request: { email, password }
  Response: { access_token, refresh_token, expires_in }
  Status: 200, 401, 500

POST /api/auth/refresh
  Request: { refresh_token }
  Response: { access_token, expires_in }
  Status: 200, 401, 500
```

#### Health Endpoints
```
GET /api/health
  Response: { status, service, version }
  Status: 200

GET /api/status
  Response: { status, service, version, timestamp }
  Status: 200
```

---

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────────┐
│         User Login Request                  │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│  Validate Credentials                       │
│  - Email format validation                  │
│  - Password strength check                  │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│  Database Lookup                            │
│  - Find user by email                       │
│  - Verify password hash                     │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│  Generate Tokens                            │
│  - Access Token (30 min)                    │
│  - Refresh Token (7 days)                   │
└─────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────┐
│  Return Tokens to Client                    │
└─────────────────────────────────────────────┘
```

### Security Layers

1. **Input Validation**
   - Pydantic schema validation
   - Email format validation
   - Password strength requirements
   - Headline length limits
   - File size limits

2. **XSS Protection**
   - HTML escaping
   - Tag removal
   - Content Security Policy headers

3. **CORS Configuration**
   - Whitelist allowed origins
   - Restrict methods
   - Control headers

4. **Rate Limiting**
   - Per-IP rate limiting
   - Request throttling
   - Graceful degradation

5. **JWT Security**
   - Secure token generation
   - Token expiration
   - Refresh token rotation
   - Secret key management

6. **Password Security**
   - bcrypt hashing
   - Salt generation
   - Complexity requirements

---

## Scalability & Performance

### Performance Optimization

#### Frontend
- Code splitting with React.lazy()
- Image lazy loading
- CSS minification
- Bundle size optimization
- Caching strategies

#### Backend
- Async/await for non-blocking I/O
- Database connection pooling
- Query optimization with indexes
- Response caching
- Model inference optimization

#### Database
- Indexes on frequently queried fields
- Pagination for large datasets
- Aggregation pipelines
- Connection pooling

### Scalability Strategies

#### Horizontal Scaling
```
Load Balancer
    ├─ Backend Instance 1
    ├─ Backend Instance 2
    └─ Backend Instance 3
         ↓
    MongoDB Replica Set
         ├─ Primary
         ├─ Secondary 1
         └─ Secondary 2
```

#### Caching Layer
- Redis for session caching
- Model inference caching
- Query result caching
- API response caching

#### Database Optimization
- Sharding strategy (by user_id)
- Read replicas for analytics
- Archive old analyses
- Backup strategy

---

## Deployment Architecture

### Local Development
```
docker-compose up
    ├─ MongoDB (port 27017)
    ├─ Backend (port 8000)
    └─ Frontend (port 3000)
```

### Production Deployment

#### Backend (Render/Railway)
```
GitHub Repository
    ↓
GitHub Actions CI/CD
    ├─ Run Tests
    ├─ Code Quality Checks
    └─ Build Docker Image
    ↓
Deploy to Render/Railway
    ├─ Pull Docker Image
    ├─ Start Container
    └─ Health Check
    ↓
MongoDB Atlas Connection
```

#### Frontend (Vercel)
```
GitHub Repository
    ↓
Vercel Deployment
    ├─ Install Dependencies
    ├─ Build (pnpm run build)
    └─ Deploy to CDN
    ↓
Environment Variables
    └─ VITE_API_URL
```

#### Database (MongoDB Atlas)
```
MongoDB Atlas Cluster
    ├─ Replication Set (3 nodes)
    ├─ Automated Backups
    ├─ IP Whitelist
    └─ SSL/TLS Encryption
```

---

## Error Handling & Resilience

### Error Categories

#### Client Errors (4xx)
- 400: Bad Request (validation error)
- 401: Unauthorized (auth failure)
- 403: Forbidden (permission denied)
- 404: Not Found (resource not found)
- 429: Too Many Requests (rate limit)

#### Server Errors (5xx)
- 500: Internal Server Error
- 502: Bad Gateway
- 503: Service Unavailable

### Error Handling Strategy

```
Request
    ↓
Try-Catch Block
    ├─ Validation Error
    │   └─ Return 400 + Message
    ├─ Authentication Error
    │   └─ Return 401 + Message
    ├─ Database Error
    │   └─ Retry Logic → Return 500
    ├─ Model Error
    │   └─ Fallback → Return 500
    └─ Unexpected Error
        └─ Log + Return 500
```

### Resilience Patterns

1. **Retry Logic**
   - Exponential backoff
   - Max retries: 3
   - Timeout: 30 seconds

2. **Circuit Breaker**
   - Fail fast on repeated errors
   - Automatic recovery
   - Fallback responses

3. **Timeouts**
   - API request timeout: 30s
   - Database query timeout: 10s
   - Model inference timeout: 60s

4. **Graceful Degradation**
   - Skip image analysis if failed
   - Use cached models
   - Provide partial results

---

## Monitoring & Observability

### Logging Strategy

```
┌─────────────────────────────────────────┐
│  Structured Logging (JSON Format)       │
├─────────────────────────────────────────┤
│  - Request logs                         │
│  - Response logs                        │
│  - Error logs                           │
│  - Database operation logs              │
│  - Model inference logs                 │
│  - User action logs                     │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  Log Aggregation                        │
│  - Local files (logs/)                  │
│  - Cloud logging (optional)             │
│  - Error tracking (Sentry)              │
└─────────────────────────────────────────┘
```

### Metrics

- Request count and latency
- Error rate
- Model inference time
- Database query time
- Cache hit rate
- User authentication attempts

### Health Checks

```
GET /api/health
    ├─ Database connectivity
    ├─ Model availability
    └─ Service status

GET /api/status
    ├─ Timestamp
    ├─ Version
    └─ Uptime
```

---

## Future Enhancements

### Phase 2: Advanced Features
- User authentication UI
- Advanced analytics
- Collaboration features
- API integrations
- Model versioning

### Phase 3: Enterprise Features
- Multi-tenancy
- Custom models
- Advanced reporting
- Audit logging
- SSO integration

### Phase 4: Scale & Optimize
- Microservices architecture
- Kubernetes deployment
- Advanced caching
- Database sharding
- Real-time updates

---

**Document Version**: 1.0.0
**Last Updated**: January 2024
**Status**: Complete System Design
