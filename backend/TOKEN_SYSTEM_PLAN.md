# Token System Implementation Plan

## Overview
Add token-based access control to the donation certificate app to ensure only valid donors can generate certificates.

## Architecture

### System Components
1. **Frontend (GitHub Pages)**: Existing certificate app with minimal token validation
2. **Backend (Render.com)**: Python Flask API + PostgreSQL for token management
3. **CRM Integration**: Token generation for donors

### Token Flow
```
Donation → CRM generates tokens → Donor receives URL → Token validation → Certificate generation → Token consumed
```

## Specification

### 1. Token Generation & Distribution
- CRM generates unique tokens per donation
- Multiple tokens per donor based on donation amount
- URL format: `https://rubensmau.github.io/certificate/?token=<unique_value>`
- Tokens use cryptographically secure random generation (UUID4)

### 2. Certificate Program Changes
**Token Validation Flow:**
1. Extract token from URL parameter
2. Validate token with API call
3. If valid → show certificate UI
4. If invalid → redirect to donation page
5. On successful download → mark token as used

**Two-stage Token Lifecycle (prevents accidental loss):**
- `UNUSED` → `IN_USE` (on validation)
- `IN_USE` → `COMPLETED` (on successful download)
- Only `COMPLETED` tokens are deleted

### 3. Token Management API

**Endpoints:**
```
POST /tokens          # CRM creates new tokens
GET /tokens/{token}   # Validate token + mark IN_USE
DELETE /tokens/{token} # Mark token as COMPLETED
GET /tokens           # List all tokens (admin)
```

**Database Schema:**
```sql
CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'UNUSED',
    created_at TIMESTAMP DEFAULT NOW(),
    used_at TIMESTAMP
);
```

## Implementation Plan

### Phase 1: Backend API (Render.com)
**Tech Stack:**
- Python Flask (lightweight, familiar)
- PostgreSQL (Render managed database)
- Flask-CORS for GitHub Pages integration

**Files needed:**
- `app.py` - Main Flask application
- `requirements.txt` - Dependencies
- `models.py` - Database models
- `config.py` - Environment configuration

### Phase 2: Frontend Integration
**Minimal changes to existing certificate app:**
- Add token validation function on page load
- Add API call to mark token as used on download
- Add redirect logic for invalid tokens

**Required changes:**
```javascript
// Token validation (add to existing JS)
async function validateToken() {
  const token = new URLSearchParams(window.location.search).get('token');
  if (!token) return redirectToDonation();
  
  const response = await fetch(`${API_BASE_URL}/tokens/${token}`);
  if (!response.ok) return redirectToDonation();
  
  enableCertificateGeneration();
}

// Mark token as used (call after successful download)
async function markTokenUsed(token) {
  await fetch(`${API_BASE_URL}/tokens/${token}`, { method: 'DELETE' });
}
```

### Phase 3: Deployment
**Render.com Setup:**
1. Create new web service
2. Connect to GitHub repository
3. Add PostgreSQL database
4. Configure environment variables
5. Set up auto-deploy

**Integration:**
1. Configure CORS for GitHub Pages domain
2. Update frontend with API endpoint URL
3. Test token flow end-to-end

## Security Considerations
- Cryptographically secure token generation
- HTTPS enforced (included with Render)
- Rate limiting on API endpoints
- Token expiration (30 days recommended)
- Audit logging for token usage

## Edge Cases & Solutions
1. **Accidental download**: Two-stage token lifecycle prevents loss
2. **Network failures**: Retry logic + idempotent operations
3. **Race conditions**: Database-level constraints
4. **Browser refresh**: Token state persists until actual completion

## Deployment Timeline
- **Week 1**: Backend API development and testing
- **Week 2**: Frontend integration and CORS setup
- **Week 3**: Render deployment and end-to-end testing
- **Week 4**: CRM integration and go-live

## Cost Estimation
- Render.com: $7/month for web service + $7/month for PostgreSQL
- Total: ~$14/month for short-term deployment
- Can be scaled down or paused when not in use

## Next Steps
1. Set up Render.com account and GitHub integration
2. Implement Flask API with token endpoints
3. Add PostgreSQL database and models
4. Test API locally before deployment
5. Integrate with existing frontend application

---
*Plan created: 2025-01-08*
*Status: Ready for implementation*