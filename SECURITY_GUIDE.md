# Security Guide - Fake News Detector

## Security Overview

This guide covers all security aspects of the Fake News & Misinformation Detector application, including authentication, authorization, data protection, and deployment security.

---

## 1. Authentication & Authorization

### JWT Implementation

**Token Structure**:
```
Header: { alg: "HS256", typ: "JWT" }
Payload: { user_id, email, exp, token_type }
Signature: HMACSHA256(header.payload, SECRET_KEY)
```

**Token Lifecycle**:
- Access Token: 30 minutes validity
- Refresh Token: 7 days validity
- Token Refresh: Automatic when expired

**Best Practices**:
- Store tokens in secure HTTP-only cookies (frontend)
- Never expose tokens in URLs
- Implement token rotation
- Use strong secret keys (32+ characters)
- Change secret keys in production

### Password Security

**Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- Optional special characters

**Hashing**:
- Algorithm: bcrypt
- Cost factor: 12
- Salt: Automatically generated

**Implementation**:
```python
from app.security.auth import PasswordHasher

# Hash password
hashed = PasswordHasher.hash_password("UserPassword123!")

# Verify password
is_valid = PasswordHasher.verify_password("UserPassword123!", hashed)
```

### Role-Based Access Control (RBAC)

**Roles**:
- `user`: Standard user (default)
- `admin`: Administrator access
- `analyst`: Data analyst access

**Implementation**:
```python
from app.security.dependencies import verify_admin_role

@router.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str, admin = Depends(verify_admin_role)):
    # Only admins can access
    pass
```

---

## 2. Input Validation & Sanitization

### Validation Rules

**Headline**:
- Length: 3-1000 characters
- No null bytes
- No control characters
- Whitespace normalized

**Email**:
- RFC 5322 format
- Maximum 255 characters
- Lowercase normalized

**Image URL**:
- Valid HTTP/HTTPS URL
- Allowed extensions: jpg, jpeg, png, gif, webp
- File size: < 10MB

**File Upload**:
- Maximum size: 10MB
- Allowed MIME types: image/*
- Virus scanning recommended

### XSS Protection

**HTML Escaping**:
```python
from app.utils.validators import XSSProtection

# Escape HTML
safe_text = XSSProtection.escape_html(user_input)

# Remove tags
clean_text = XSSProtection.remove_html_tags(user_input)
```

**Content Security Policy Headers**:
```
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
```

### SQL Injection Prevention

**MongoDB Protection**:
- Use parameterized queries (automatic with Motor)
- Validate input types
- Avoid string concatenation in queries
- Use schema validation

**Example**:
```python
# Safe
user = await db.users.find_one({"email": email})

# Unsafe (avoid)
query = f"db.users.find_one({{'email': '{email}'}})"
```

---

## 3. Data Protection

### Encryption at Rest

**Implementation**:
- MongoDB encryption: Enable in Atlas
- Database user credentials: Use environment variables
- Sensitive data: Encrypt before storage

**Configuration**:
```
MongoDB Atlas → Security → Encryption at Rest
Enable: Automatic encryption with AWS KMS
```

### Encryption in Transit

**HTTPS/TLS**:
- Minimum TLS 1.2
- Valid SSL certificates
- HSTS headers enabled

**Implementation**:
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

### Data Masking

**Sensitive Fields**:
- Passwords: Never log or display
- Email: Mask in logs (user@*****.com)
- IP addresses: Hash or anonymize
- API keys: Mask in logs

**Implementation**:
```python
def mask_email(email: str) -> str:
    parts = email.split("@")
    return f"{parts[0][:2]}***@{parts[1]}"
```

---

## 4. API Security

### Rate Limiting

**Configuration**:
- Default: 100 requests per minute per IP
- Burst: 10 requests per second
- Bypass: Health check endpoints

**Implementation**:
```python
from app.middleware.rate_limit import rate_limiter

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Rate limiting logic
    pass
```

### CORS Configuration

**Allowed Origins**:
```python
allowed_origins = [
    "http://localhost:5173",      # Development
    "https://yourdomain.com",     # Production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

### API Key Management

**Implementation**:
- Store in environment variables
- Rotate regularly (monthly)
- Use separate keys for different environments
- Monitor key usage

**Example**:
```python
GOOGLE_FACT_CHECK_API_KEY = os.getenv("GOOGLE_FACT_CHECK_API_KEY")

if not GOOGLE_FACT_CHECK_API_KEY:
    raise ValueError("API key not configured")
```

### Request Validation

**Headers**:
- Validate Content-Type
- Check User-Agent
- Verify Origin

**Body**:
- Validate JSON structure
- Check field types
- Enforce size limits

---

## 5. Authentication Flows

### User Registration

```
1. User submits email and password
2. Validate email format
3. Check email not already registered
4. Validate password strength
5. Hash password with bcrypt
6. Store user in database
7. Return success message
```

### User Login

```
1. User submits email and password
2. Validate input format
3. Query database for user
4. Verify password hash
5. Check user is active
6. Generate JWT tokens
7. Update last_login timestamp
8. Return tokens to client
```

### Token Refresh

```
1. Client submits refresh token
2. Verify token signature
3. Check token type is "refresh"
4. Check token not expired
5. Generate new access token
6. Return new access token
```

---

## 6. Error Handling Security

### Safe Error Messages

**Do's**:
- Generic error messages for users
- Detailed logs for developers
- No sensitive data in responses
- Consistent error format

**Don'ts**:
- Don't expose stack traces
- Don't reveal database structure
- Don't show file paths
- Don't leak user information

**Example**:
```python
# Bad
raise HTTPException(detail=f"User {email} not found")

# Good
raise HTTPException(detail="Invalid credentials")
```

### Logging Security

**What to Log**:
- Authentication attempts
- Authorization failures
- API errors
- Data modifications
- Suspicious activities

**What NOT to Log**:
- Passwords
- API keys
- Credit card numbers
- Personal identification
- Sensitive user data

---

## 7. Dependency Security

### Vulnerability Scanning

```bash
# Check for vulnerabilities
safety check

# Detailed report
safety check --json

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Dependency Management

**Best Practices**:
- Pin specific versions
- Regular updates (monthly)
- Security patches immediately
- Test after updates
- Use virtual environments

**requirements.txt**:
```
# Pin specific versions
fastapi==0.104.1
pydantic==2.5.0
pymongo==4.6.0
```

---

## 8. Deployment Security

### Environment Variables

**Never Commit**:
```
.env
.env.local
.env.production
```

**Use**:
- Environment variable files
- Secrets management services
- CI/CD secret management
- Cloud provider secret stores

**Example**:
```bash
# Set environment variable
export JWT_SECRET="your-secret-key"

# Use in code
jwt_secret = os.getenv("JWT_SECRET")
```

### Docker Security

**Best Practices**:
- Use minimal base images
- Don't run as root
- Scan images for vulnerabilities
- Use secrets management

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Don't run as root
RUN useradd -m appuser
USER appuser

# Copy only necessary files
COPY --chown=appuser:appuser . .
```

### Database Security

**MongoDB Atlas**:
- Enable authentication
- Use strong passwords
- IP whitelist
- Enable encryption
- Regular backups
- Monitor access logs

**Connection String**:
```
mongodb+srv://username:password@cluster.mongodb.net/database?
  authSource=admin&
  ssl=true&
  retryWrites=true&
  w=majority
```

---

## 9. Frontend Security

### Content Security Policy

```html
<meta http-equiv="Content-Security-Policy" 
  content="default-src 'self'; script-src 'self' 'unsafe-inline'">
```

### Secure Headers

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### Local Storage Security

**Don't Store**:
- Passwords
- API keys
- Sensitive tokens
- Personal data

**Store**:
- Session tokens (HTTP-only cookies)
- User preferences
- Non-sensitive data

---

## 10. Security Checklist

### Before Deployment

- [ ] All secrets in environment variables
- [ ] HTTPS/TLS enabled
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] XSS protection enabled
- [ ] CSRF tokens implemented
- [ ] SQL injection prevention
- [ ] Authentication tested
- [ ] Authorization tested
- [ ] Error messages safe
- [ ] Logs don't contain secrets
- [ ] Dependencies scanned
- [ ] Security headers set
- [ ] Database encrypted
- [ ] Backups configured
- [ ] Monitoring enabled
- [ ] Incident response plan

### Regular Maintenance

- [ ] Monthly dependency updates
- [ ] Weekly security log review
- [ ] Quarterly penetration testing
- [ ] Annual security audit
- [ ] Regular backup testing
- [ ] Password rotation (90 days)
- [ ] API key rotation (monthly)
- [ ] Certificate renewal (before expiry)

---

## 11. Incident Response

### Security Incident Steps

1. **Detect**: Monitor logs and alerts
2. **Assess**: Determine severity and scope
3. **Contain**: Isolate affected systems
4. **Eradicate**: Remove the threat
5. **Recover**: Restore normal operations
6. **Document**: Record incident details
7. **Improve**: Update security measures

### Emergency Contacts

- Security Team: security@example.com
- Database Admin: dba@example.com
- DevOps Team: devops@example.com

---

## 12. Security Resources

### Tools

- **OWASP ZAP**: Web application security scanner
- **Bandit**: Python security linter
- **Safety**: Python dependency checker
- **Snyk**: Vulnerability scanner
- **Trivy**: Container image scanner

### References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)

---

**Security Guide Version**: 1.0.0
**Last Updated**: January 2024
**Status**: Production Ready
