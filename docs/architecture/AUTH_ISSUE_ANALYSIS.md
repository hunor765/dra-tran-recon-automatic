# DRA Platform Authentication Issue - Root Cause Analysis

> **Status**: INVESTIGATING  
> **Last Updated**: 2026-02-23  
> **Severity**: CRITICAL - Production authentication is broken  
> **Assigned**: TBD

---

## Executive Summary

The DRA Transaction Reconciliation Platform has a **critical authentication failure** in production. Users can log in via the frontend (Supabase Auth works), but all API calls to the backend return **401 Unauthorized**. This renders the application completely unusable.

### Current Behavior
- ✅ Frontend login works (Supabase Auth session created)
- ✅ Frontend has valid JWT token (ES256 algorithm)
- ❌ Backend rejects all tokens with "Invalid or expired token"
- ❌ Users cannot access any data or functionality

---

## Evidence & Logs

### Token Characteristics
From debug endpoint and logs:
```json
{
  "algorithm": "ES256",
  "kid": "26bd5c72-1304-4d3b-afb0-15dad4da7f6a",
  "token_preview": "eyJhbGciOiJFUzI1NiIsImtpZCI6Ij...",
  "expires_at": "2026-02-23T10:05:47.000Z",
  "is_expired": false
}
```

### Backend Log Analysis
From `railway_logs/logs.1771841151347.json`:

```
2026-02-23 10:05:34 [INFO ] Token uses ES256 - attempting JWKS validation
2026-02-23 10:05:34 [INFO ] JWKS fetched successfully with 1 keys
2026-02-23 10:05:34 [INFO ] Found matching key with kid '26bd5c72-...', type 'EC'
2026-02-23 10:05:34 [ERROR] Error converting EC JWK to PEM: name 'serialization' is not defined
2026-02-23 10:05:34 [WARN ] Could not extract public key for kid '...' from JWKS
2026-02-23 10:05:34 [INFO ] Falling back to Supabase Auth API for validation
2026-02-23 10:05:34 [INFO ] Calling Supabase Auth API: https://romfgsniplxaslzndiki.supabase.co/auth/v1/user
2026-02-23 10:05:34 [INFO ] HTTP Request: GET .../auth/v1/user "HTTP/1.1 401 Unauthorized"
2026-02-23 10:05:34 [WARN ] Token validation failed: Invalid or expired token
```

**Key Finding**: TWO separate failures are occurring:
1. **JWKS validation fails** due to missing import (`serialization` not defined)
2. **Supabase Auth API fallback also fails** with 401

---

## Problem Decomposition

### Issue #1: JWKS Public Key Conversion Bug

**Location**: `apps/platform/backend/core/auth.py`  
**Function**: `_convert_ec_jwk_to_pem()`

**Root Cause**: Missing import statement. The function uses `serialization` module but it's not imported in the helper function scope.

```python
# Current imports at top of file:
from cryptography.hazmat.primitives import serialization  # ✅ Present

# But inside _convert_ec_jwk_to_pem():
pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,  # ❌ NameError: 'serialization' not defined
    ...
)
```

**Why this happens**: Python scoping issue. The nested function doesn't inherit imports properly, or the import was accidentally removed during refactoring.

**Impact**: High - prevents local JWT validation

---

### Issue #2: Supabase Auth API Returns 401

**Location**: `apps/platform/backend/core/auth.py`  
**Function**: `_validate_token_with_supabase()` (fallback path)

**API Call**:
```python
GET https://romfgsniplxaslzndiki.supabase.co/auth/v1/user
Headers:
  Authorization: Bearer <token>
  apikey: <SUPABASE_ANON_KEY>
```

**Question**: Why does this return 401?

**Hypotheses**:
1. **Wrong API key**: The `SUPABASE_ANON_KEY` env var might be incorrect/mismatched
2. **Token issuer mismatch**: The token was issued by a different Supabase project
3. **API version change**: Supabase may have changed the auth endpoint
4. **Service role required**: The `/auth/v1/user` endpoint might need service_role key instead of anon key
5. **Token format issue**: The token might need to be sent differently

**Evidence to collect**:
- What Supabase project is the frontend using vs backend?
- Is the ANON_KEY the same in both frontend and backend?
- Can we test the API call manually with curl?

---

## Architecture Context

### Authentication Flow
```
┌──────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Frontend   │         │  Supabase Auth   │         │  Backend API    │
│  (Next.js)   │────────▶│  ( auth/users )  │◄────────│  (FastAPI)      │
└──────────────┘         └──────────────────┘         └─────────────────┘
       │                           │                           │
       │ 1. User logs in           │                           │
       │──────────────────────────▶│                           │
       │                           │                           │
       │ 2. JWT token returned     │                           │
       │◄──────────────────────────│                           │
       │                           │                           │
       │ 3. API call with token    │                           │
       │───────────────────────────────────────────────────────▶│
       │                           │                           │
       │                           │ 4. Validate token         │
       │                           │◄──────────────────────────│
       │                           │                           │
       │                           │ 5. User data or 401       │
       │                           │──────────────────────────▶│
       │                           │                           │
       │ 6. Response (fails here)  │                           │
       │◄───────────────────────────────────────────────────────│
```

### Validation Methods Tried (in order)
1. **JWKS Local Validation** (preferred, faster)
   - Fetch JWKS from `/.well-known/jwks.json`
   - Find key matching token's `kid`
   - Convert JWK to PEM
   - Verify signature locally
   - ❌ Currently fails due to missing import

2. **Supabase Auth API** (fallback)
   - Call `GET /auth/v1/user` with token
   - Supabase validates and returns user info
   - ❌ Currently returns 401 (root cause unknown)

3. **JWT Secret** (HS256 only)
   - Use shared secret for symmetric validation
   - Only works for HS256 tokens
   - ❌ Not applicable (tokens are ES256)

---

## Environment Configuration

### Frontend (Environment Variables)
```
NEXT_PUBLIC_SUPABASE_URL=https://romfgsniplxaslzndiki.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<frontend-anon-key>
NEXT_PUBLIC_API_URL=https://dra-tran-recon-automatic-production.up.railway.app
```

### Backend (Environment Variables)
```
SUPABASE_URL=https://romfgsniplxaslzndiki.supabase.co
SUPABASE_ANON_KEY=<backend-anon-key>
SUPABASE_JWT_SECRET=<set-but-unused-for-es256>
```

**CRITICAL QUESTION**: Are the `SUPABASE_ANON_KEY` values identical between frontend and backend?

---

## Questions for Investigation

### High Priority
1. **Are frontend and backend using the same Supabase project?**
   - Compare URLs in browser dev tools vs backend logs
   
2. **What is the exact 401 response from Supabase?**
   - Add response body logging to see error details
   
3. **Is the ANON_KEY correct in Railway?**
   - Check Railway dashboard environment variables
   - Compare with Supabase Dashboard → Project Settings → API

4. **Can we manually test the API?**
   ```bash
   curl -X GET \
     https://romfgsniplxaslzndiki.supabase.co/auth/v1/user \
     -H "Authorization: Bearer <token-from-browser>" \
     -H "apikey: <anon-key-from-railway>"
   ```

### Medium Priority
5. **Should we use Service Role Key instead?**
   - Some Supabase endpoints require `service_role` key
   - Check Supabase documentation for `/auth/v1/user`

6. **Is there an alternative validation endpoint?**
   - `/auth/v1/token`?
   - Supabase Python client library?

7. **Can we extract the JWT secret from Supabase?**
   - Some Supabase projects allow accessing JWT secret for local validation
   - This would bypass both issues entirely

---

## Potential Solutions

### Solution A: Fix the Import Bug (Immediate)
**Effort**: Low (1 line fix)  
**Impact**: Enables JWKS validation path

Add missing import or use module-level function:
```python
# Option 1: Add import inside function
def _convert_ec_jwk_to_pem(key: Dict[str, Any]) -> Optional[str]:
    from cryptography.hazmat.primitives import serialization  # Add this
    ...

# Option 2: Pass serialization as parameter
# Option 3: Move function to module level where import is visible
```

**Pros**: Fast fix, proper ES256 validation  
**Cons**: Doesn't explain why fallback also fails

---

### Solution B: Fix Supabase Auth API Call
**Effort**: Medium (requires investigation)  
**Impact**: Makes fallback work

Investigate and fix the 401:
- Verify ANON_KEY is correct
- Try Service Role Key instead
- Check if endpoint URL is correct

**Pros**: Robust fallback  
**Cons**: Requires network call for every request (slower)

---

### Solution C: Switch to HS256 Tokens
**Effort**: Medium (requires Supabase config change)  
**Impact**: Works with existing JWT_SECRET validation

Configure Supabase to issue HS256 tokens instead of ES256:
- Update Supabase project settings
- Use JWT_SECRET for local validation

**Pros**: Simple, fast, no external calls  
**Cons**: Less secure (symmetric), requires Supabase changes

---

### Solution D: Use Supabase Python Client
**Effort**: Medium (library integration)  
**Impact**: Official validation method

Replace custom validation with Supabase Python client:
```python
from supabase import create_client
supabase = create_client(url, key)
user = supabase.auth.get_user(token)
```

**Pros**: Official, maintained, handles edge cases  
**Cons**: Adds dependency, might have same 401 issue

---

## Recommended Next Steps

### Immediate (Before Any Code Changes)
1. **Verify Environment Variables**
   - Check Railway dashboard for `SUPABASE_ANON_KEY`
   - Compare with Supabase Dashboard → Settings → API
   - Ensure frontend and backend use same project

2. **Manual API Test**
   - Get token from browser (Network tab or debug page)
   - Test Supabase API with curl
   - Document exact error response

3. **Add Detailed Logging**
   - Log full Supabase API response body
   - Log which ANON_KEY is being used (prefix)
   - Log token issuer claim

### Short Term
4. **Fix the Import Bug** (Solution A)
   - One-line fix to enable JWKS validation
   - Deploy and test

5. **If still failing, implement Solution D**
   - Use Supabase Python client as fallback

### Long Term
6. **Add comprehensive auth tests**
7. **Document Supabase configuration requirements**
8. **Consider adding auth provider abstraction**

---

## Files Involved

| File | Purpose | Lines of Interest |
|------|---------|-------------------|
| `apps/platform/backend/core/auth.py` | Main auth logic | `_validate_token_with_supabase()`, `_convert_ec_jwk_to_pem()` |
| `apps/platform/backend/core/config.py` | Environment variables | `SUPABASE_URL`, `SUPABASE_ANON_KEY` |
| `apps/platform/frontend/src/lib/api/client.ts` | Frontend API client | Token retrieval, request headers |
| `apps/platform/frontend/src/lib/supabase/client.ts` | Supabase client | Browser client initialization |
| `apps/platform/frontend/middleware.ts` | Frontend auth | Route protection, role checking |
| `apps/platform/backend/api/v1/endpoints/debug.py` | Debug endpoints | Token validation testing |

---

## Related Documentation

- `docs/platform/SUPABASE_SETUP.md` - Data model and setup guide
- `docs/DEVELOPER_GUIDE.md` - Developer setup instructions
- `docs/API_MAP.md` - API endpoint reference

---

## Appendix: Raw Log Samples

### Full JWKS Response (from logs)
```
JWKS fetched successfully with 1 keys
Key: kid=26bd5c72-1304-4d3b-afb0-15dad4da7f6a, kty=EC, crv=P-256
```

### Token Header Decoded
```json
{
  "alg": "ES256",
  "kid": "26bd5c72-1304-4d3b-afb0-15dad4da7f6a",
  "typ": "JWT"
}
```

### Token Payload Decoded
```json
{
  "aud": "authenticated",
  "exp": 1708680000,
  "iat": 1708676400,
  "sub": "0cd3b106-e3a0-44e6-b309-eb6ec7d8fae6",
  "email": "hunor.lazar@datarevolt.agency",
  "role": "authenticated"
}
```

---

## Discussion & Challenges

**Agent 1**: Should we just fix the import bug and deploy?

**Agent 2**: But that doesn't explain why the Supabase API fallback also fails. We should understand the root cause of the 401 first.

**Agent 3**: The 401 might be because the ANON_KEY in Railway is wrong. Let's verify environment variables before making code changes.

**Agent 4**: Could we also consider using the Supabase Python client library instead of custom JWT validation? It might handle edge cases better.

**Consensus Needed**:
1. Verify environment variables first
2. Decide between fixing current code vs. switching to Supabase client
3. Determine if we need Service Role Key vs ANON_KEY

---

*This document should be updated as investigation progresses. All agents should read this before attempting any fixes.*
