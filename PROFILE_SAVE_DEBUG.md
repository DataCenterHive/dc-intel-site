# Profile Save Debugging Guide

## The Issue

When you click "Save Changes", you see:
```
ℹ️ Profile Saved Locally: Profile saving to server isn't enabled yet. Your changes are saved on this device only.
```

This means the backend endpoint is **not working** and the frontend is falling back to localStorage.

---

## 🔍 Step-by-Step Debugging

### Step 1: Open DevTools Network Tab

1. Open account settings page
2. Press **F12** to open DevTools
3. Click **Network** tab
4. **Clear** any existing requests (trash icon)
5. Click **"Save Changes"** button
6. Look for a request to `/api/auth/profile`

---

### Step 2: Check the Request

**Look for these details:**

#### A) Request URL
**What it should be:**
```
https://dc-intel-api.onrender.com/api/auth/profile
```

**Check:**
- ✅ Correct domain? (`dc-intel-api.onrender.com`)
- ✅ Correct path? (`/api/auth/profile`)
- ✅ HTTPS not HTTP?
- ✅ No typos?

**Copy the EXACT URL** from DevTools and paste it here: _______________

---

#### B) Request Method
**Should be:** `PATCH`

**If it's not PATCH:**
- GET → Frontend bug (wrong method)
- POST → Frontend bug (wrong method)
- OPTIONS → CORS preflight (check next step)

---

#### C) Request Headers
**Click on the request → Headers tab**

Look for:
```
Authorization: Bearer eyJ...
Content-Type: application/json
```

**Check:**
- ✅ Has `Authorization` header?
- ✅ Token value looks right? (starts with `eyJ` or similar)
- ✅ Has `Content-Type: application/json`?

**If Authorization is missing:**
- Frontend bug - token not being sent
- Check: `localStorage.getItem('dc_intel_token')` in Console

**If Authorization is there but weird:**
- Wrong format (should be `Bearer <token>`, not just `<token>`)

---

#### D) Request Payload
**Click on the request → Payload tab**

**Should look like:**
```json
{
  "full_name": "Your Name",
  "company": "Your Company",
  "job_title": "Your Title"
}
```

**If payload is missing or wrong:**
- Frontend bug
- Check form values

---

#### E) Response Status Code

**Possible statuses and what they mean:**

| Status | Meaning | Fix |
|--------|---------|-----|
| **404 Not Found** | Endpoint doesn't exist | Backend needs to implement `PATCH /api/auth/profile` |
| **405 Method Not Allowed** | Endpoint exists but doesn't accept PATCH | Backend configured for GET/POST only |
| **401 Unauthorized** | Token invalid/expired | Get new token by logging in again |
| **403 Forbidden** | Token valid but not allowed | Backend permission issue |
| **500 Internal Server Error** | Backend crashed | Check backend logs |
| **502 Bad Gateway** | Backend down/unreachable | Check if Render.com service is running |
| **CORS error** | Backend not allowing GitHub Pages | Backend needs CORS headers |

**Your status code:** _______________

---

#### F) Response Body
**Click on the request → Response tab**

**Copy the EXACT response** here: _______________

Common responses:

**404:**
```json
{"detail": "Not Found"}
```
→ Endpoint doesn't exist

**401:**
```json
{"detail": "Could not validate credentials"}
```
→ Token expired or invalid

**CORS error in Console:**
```
Access to fetch at 'https://...' from origin 'https://datacenterhive.github.io'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header
```
→ Backend needs to add CORS headers

---

### Step 3: Console Errors

**Look in the Console tab for errors**

**Common errors:**

```javascript
// CORS error
Access to fetch at '...' has been blocked by CORS policy
```
→ Backend needs CORS configuration

```javascript
// Network error
Failed to fetch
TypeError: Failed to fetch
```
→ Backend is down or unreachable

```javascript
// Token missing
Not Authenticated: Please log in again
```
→ Token was cleared or expired

---

## 🔧 Common Fixes

### Fix 1: Endpoint Doesn't Exist (404)

**Backend developer needs to add:**

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ProfileUpdate(BaseModel):
    full_name: str
    company: str | None = None
    job_title: str | None = None

@router.patch("/api/auth/profile")
async def update_profile(
    profile: ProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    # Update user in database
    current_user.full_name = profile.full_name
    current_user.company = profile.company
    current_user.job_title = profile.job_title

    db.commit()
    db.refresh(current_user)

    # Return updated user
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company": current_user.company,
        "job_title": current_user.job_title,
        "tier": current_user.tier,
        "subscription_status": current_user.subscription_status,
        # ... other fields
    }
```

---

### Fix 2: CORS Not Configured

**Backend needs CORS headers:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://datacenterhive.github.io",
        "http://localhost:3000"  # For local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Fix 3: Wrong API_BASE in Frontend

**Check `docs/dashboard/user.html` line 657:**

```javascript
const API_BASE = 'https://dc-intel-api.onrender.com';
```

**Should match your actual backend URL:**
- ✅ Production: `https://dc-intel-api.onrender.com`
- ✅ Staging: `https://dc-intel-api-staging.onrender.com`
- ✅ Local: `http://localhost:8000`

**If wrong, update it.**

---

### Fix 4: Token Expired

**Get a new token:**
1. Log out
2. Log in again
3. Try saving profile again

**Check token in Console:**
```javascript
localStorage.getItem('dc_intel_token')
```

Should return a long string starting with `eyJ...` (if JWT) or similar.

---

## 🧪 Quick Test (Backend is Ready)

To test if backend is working WITHOUT the frontend:

### Using curl:
```bash
curl -X PATCH https://dc-intel-api.onrender.com/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","company":"Test Co","job_title":"Tester"}'
```

**Expected response:**
```json
{
  "email": "your@email.com",
  "full_name": "Test User",
  "company": "Test Co",
  "job_title": "Tester",
  ...
}
```

### Using Python:
```python
import requests

token = "YOUR_TOKEN_HERE"
url = "https://dc-intel-api.onrender.com/api/auth/profile"

response = requests.patch(
    url,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "full_name": "Test User",
        "company": "Test Co",
        "job_title": "Tester"
    }
)

print(response.status_code)
print(response.json())
```

---

## ✅ Checklist

- [ ] Opened DevTools Network tab
- [ ] Clicked "Save Changes"
- [ ] Found the PATCH request to `/api/auth/profile`
- [ ] Copied the exact URL
- [ ] Noted the status code
- [ ] Copied the response body
- [ ] Checked for CORS errors in Console
- [ ] Verified Authorization header is present
- [ ] Checked if backend is running (visit API docs at `/docs`)

---

## 📊 Report Template

Copy this and fill it out:

```
**Request URL:**
_______________

**Request Method:**
_______________

**Status Code:**
_______________

**Authorization Header Present?**
Yes / No

**Response Body:**
_______________

**Console Errors:**
_______________

**Backend Status:**
- [ ] Backend is running (checked /docs endpoint)
- [ ] Backend has PATCH /api/auth/profile endpoint
- [ ] Backend has CORS configured
```

With this information, we can pinpoint exactly what's wrong!

---

## 🔄 Should I Remove the Fallback?

**Options:**

### Option A: Remove fallback entirely
```javascript
if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update profile');
}
// No fallback - just shows error
```

**Pros:** Forces backend to be working
**Cons:** Breaks during backend downtime

### Option B: Keep fallback as "offline mode"
```javascript
if (!response.ok) {
    if (response.status === 404 || response.status === 501) {
        // Save locally as fallback
        showBanner('warning', 'Offline mode: Changes saved locally only');
    } else {
        throw new Error('Failed to save');
    }
}
```

**Pros:** Works during backend issues
**Cons:** Users might not realize backend is down

### Option C: Keep fallback but make it obvious
```javascript
if (response.status === 404 || response.status === 501) {
    showBanner('error', 'Backend not ready: Saving locally. Contact support if this persists.');
}
```

**Pros:** Clear that something is wrong
**Cons:** Scary for users

**Recommendation:** Once backend is confirmed working, use **Option A** (remove fallback).
