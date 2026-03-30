# Performance Optimization Guide

## Backend Performance

### Database Optimization

**Indexes**:
```python
# Create indexes for frequently queried fields
db.analyses.create_index([("user_id", 1), ("created_at", -1)])
db.analyses.create_index([("prediction", 1)])
db.users.create_index([("email", 1)], unique=True)
```

**Query Optimization**:
```python
# Use projection to fetch only needed fields
analyses = await db.analyses.find(
    {"user_id": user_id},
    {"headline": 1, "prediction": 1, "created_at": 1}
).skip(skip).limit(limit).to_list(length=limit)

# Use aggregation for complex queries
pipeline = [
    {"$match": {"user_id": ObjectId(user_id)}},
    {"$group": {"_id": "$prediction", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
stats = await db.analyses.aggregate(pipeline).to_list(length=None)
```

**Connection Pooling**:
```python
# Motor automatically handles connection pooling
client = AsyncMongoClient(
    MONGO_URI,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=45000
)
```

### Model Optimization

**Lazy Loading**:
```python
# Load models only when needed
class AIModels:
    _roberta_model = None
    _clip_model = None

    @classmethod
    async def get_roberta_model(cls):
        if cls._roberta_model is None:
            cls._roberta_model = await cls._load_roberta()
        return cls._roberta_model
```

**Batch Processing**:
```python
# Process multiple items together
async def analyze_batch(headlines: List[str]):
    # Tokenize all at once
    tokens = tokenizer(headlines, padding=True, return_tensors="pt")
    
    # Run inference once
    outputs = model(**tokens)
    
    return outputs
```

**Model Caching**:
```python
# Cache model predictions
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_prediction(headline: str):
    # Cached prediction
    return model.predict(headline)
```

### API Response Optimization

**Pagination**:
```python
# Always paginate large datasets
@router.get("/api/history")
async def get_history(page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    items = await db.analyses.find().skip(skip).limit(limit).to_list(limit)
    total = await db.analyses.count_documents({})
    return {"items": items, "total": total, "page": page}
```

**Response Compression**:
```python
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

**Async Operations**:
```python
# Use async/await for non-blocking I/O
async def analyze_with_fact_check(headline: str):
    # Run in parallel
    text_result, fact_checks = await asyncio.gather(
        analyze_text(headline),
        get_fact_checks(headline)
    )
    return {**text_result, "fact_checks": fact_checks}
```

---

## Frontend Performance

### Code Splitting

**Route-Based Splitting**:
```typescript
import { lazy, Suspense } from 'react';

const Home = lazy(() => import('./pages/Home'));
const History = lazy(() => import('./pages/History'));
const Analytics = lazy(() => import('./pages/Analytics'));

export function Router() {
  return (
    <Suspense fallback={<Loader />}>
      <Routes>
        <Route path="/" component={Home} />
        <Route path="/history" component={History} />
        <Route path="/analytics" component={Analytics} />
      </Routes>
    </Suspense>
  );
}
```

### Image Optimization

**Lazy Loading**:
```typescript
<img 
  src="image.jpg" 
  loading="lazy"
  alt="Description"
/>
```

**Responsive Images**:
```typescript
<picture>
  <source media="(max-width: 600px)" srcSet="image-small.jpg" />
  <source media="(max-width: 1200px)" srcSet="image-medium.jpg" />
  <img src="image-large.jpg" alt="Description" />
</picture>
```

**Image Compression**:
```bash
# Use optimized images
npx imagemin src/images --out-dir=dist/images
```

### Bundle Optimization

**Tree Shaking**:
```typescript
// Good - named imports
import { Button } from '@/components/ui/button';

// Bad - default imports
import * as UI from '@/components/ui';
```

**Dynamic Imports**:
```typescript
const Chart = dynamic(() => import('recharts'), {
  loading: () => <Skeleton />,
});
```

### Caching Strategy

**HTTP Caching**:
```typescript
// Cache API responses
const cacheAPI = async (url: string) => {
  const cache = await caches.open('api-v1');
  let response = await cache.match(url);
  
  if (!response) {
    response = await fetch(url);
    cache.put(url, response.clone());
  }
  
  return response;
};
```

**Local Storage**:
```typescript
// Cache user preferences
const savePreferences = (prefs: Preferences) => {
  localStorage.setItem('preferences', JSON.stringify(prefs));
};

const loadPreferences = (): Preferences => {
  const saved = localStorage.getItem('preferences');
  return saved ? JSON.parse(saved) : defaultPrefs;
};
```

---

## Monitoring & Metrics

### Performance Metrics

**Backend**:
```python
import time

async def log_performance(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration*1000}ms")
        return result
    return wrapper
```

**Frontend**:
```typescript
// Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

### Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| API Response Time | < 200ms | - |
| Page Load Time | < 3s | - |
| Time to Interactive | < 5s | - |
| Lighthouse Score | > 90 | - |
| Bundle Size | < 500KB | - |
| Database Query | < 100ms | - |

---

## Load Testing

### Apache Bench

```bash
# Simple load test
ab -n 1000 -c 100 http://localhost:8000/api/health

# POST request
ab -n 1000 -c 100 -p data.json -T application/json \
  http://localhost:8000/api/analyze
```

### Locust

```python
from locust import HttpUser, task, between

class LoadTest(HttpUser):
    wait_time = between(1, 3)

    @task(1)
    def analyze(self):
        self.client.post("/api/analyze", json={
            "headline": "Test headline"
        })

    @task(2)
    def history(self):
        self.client.get("/api/history")
```

---

## Scaling Strategies

### Horizontal Scaling

**Load Balancer**:
```
                    Load Balancer
                    /    |    \
            Backend1  Backend2  Backend3
                    \    |    /
                  MongoDB Cluster
```

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize database queries
- Implement caching layers

### Database Sharding

```python
# Shard by user_id
shard_id = hash(user_id) % num_shards
db = get_database(shard_id)
```

---

## Optimization Checklist

- [ ] Database indexes created
- [ ] Queries optimized
- [ ] Connection pooling enabled
- [ ] Model caching implemented
- [ ] API responses paginated
- [ ] Response compression enabled
- [ ] Code splitting implemented
- [ ] Images lazy loaded
- [ ] Bundle optimized
- [ ] HTTP caching configured
- [ ] Performance monitored
- [ ] Load tests passed
- [ ] Lighthouse score > 90
- [ ] API response < 200ms
- [ ] Page load < 3s

---

**Performance Guide Version**: 1.0.0
**Last Updated**: January 2024
