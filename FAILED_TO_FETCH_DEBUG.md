# "Failed to Fetch" Error - Debugging Guide

## The Error

When clicking "Reset Password", you see:
```
Failed to fetch
```

OR in the console:
```javascript
TypeError: Failed to fetch
```

This means the browser **never got a response at all** (not even a 400/401/500).

---

## ✅ Good News: API & CORS Are Working!

I've tested your backend and **everything is configured correctly:**

### Test 1: API is Reachable
```bash
$ curl https://dc-intel-api.onrender.com/api/auth/reset-password -X POST
HTTP/2 400
{"detail":"Invalid or expired reset token"}
```
✅ API responds (400 is expected for invalid token)
✅ Endpoint exists (not 404)
✅ Returns JSON

### Test 2: CORS is Configured
```bash
$ curl -X OPTIONS \
  -H "Origin: https://datacenterhive.github.io" \
  -H "Access-Control-Request-Method: POST" \
  https://dc-intel-api.onrender.com/api/auth/reset-password

access-control-allow-origin: https://datacenterhive.github.io
access-control-allow-methods: POST
access-control-allow-headers: Content-Type
access-control-allow-credentials: true
```
✅ CORS properly configured
✅ Origin allowed: `https://datacenterhive.github.io`
✅ Method allowed: POST
✅ Headers allowed: Content-Type

### Test 3: POST Request Works
```bash
$ curl -X POST \
  -H "Origin: https://datacenterhive.github.io" \
  -H "Content-Type: application/json" \
  https://dc-intel-api.onrender.com/api/auth/reset-password

HTTP/2 400
access-control-allow-origin: https://datacenterhive.github.io
```
✅ POST request returns CORS headers
✅ No CORS blocking

---

## 🔍 So Why "Failed to Fetch"?

Since API and CORS are working, the issue is likely:

### 1. Browser Extension Blocking the Request

**Common culprits:**
- Ad blockers (uBlock Origin, AdBlock Plus)
- Privacy extensions (Privacy Badger, Ghostery)
- Security extensions
- VPN extensions

**How to test:**
1. Open **Incognito/Private window** (extensions usually disabled)
2. Try the reset password flow again
3. If it works → an extension is blocking it

**Fix:**
- Disable extensions one by one to find the culprit
- Whitelist `dc-intel-api.onrender.com` in the extension
- Or disable the extension for `datacenterhive.github.io`

### 2. Network Connectivity Issue

**Symptoms:**
- Works on curl from terminal
- Fails in browser

**Possible causes:**
- Corporate firewall blocking Render.com
- DNS resolution issue in browser
- ISP blocking the domain
- Network proxy interfering

**How to test:**
```bash
# From WSL/terminal:
curl -v https://dc-intel-api.onrender.com/api/auth/reset-password
```

If curl works but browser doesn't → network/proxy issue

**Fix:**
- Try different network (mobile hotspot)
- Check firewall settings
- Disable VPN temporarily
- Clear DNS cache: `ipconfig /flushdns` (Windows)

### 3. Browser DevTools Throttling Enabled

**How to check:**
1. Open DevTools → Network tab
2. Look for "Throttling" dropdown (usually says "No throttling")
3. If it's set to "Offline" → that's your problem!

**Fix:**
- Set throttling to "No throttling"

### 4. Mixed Content (HTTP vs HTTPS)

**Check API_BASE in reset-password.html:**
```javascript
const API_BASE = 'https://dc-intel-api.onrender.com'; // ✅ HTTPS
```

If it's `http://` (without the 's') → browsers block it

**Your code is correct** (uses HTTPS), but double-check anyway

### 5. JavaScript Error After Fetch

**The fetch might succeed, but an error in handling the response makes it look like fetch failed.**

**How to check:**
1. Open DevTools → Console
2. Look for errors AFTER you click "Reset Password"
3. Look for any errors in the response handling code

**Common issue:**
```javascript
const error = await response.json();
throw new Error(error.detail || 'Failed to reset password');
```

If `error.detail` is undefined or response isn't JSON → this throws an error

---

## 📋 Debugging Checklist

Work through these steps in order:

### Step 1: Open DevTools Network Tab

1. Open reset password page
2. Press **F12** → **Network** tab
3. Clear existing requests (trash icon)
4. Click "Reset Password"
5. **Look for the request** to `/api/auth/reset-password`

**Possible results:**

| What You See | What It Means | Fix |
|--------------|---------------|-----|
| **No request appears at all** | JavaScript didn't run OR extension blocked it | Check Console for JS errors; Try incognito |
| **OPTIONS request (red)** | CORS preflight failed | ❌ But our test shows CORS works - check extensions |
| **POST request (red)** | Request failed | Click it to see Status/Response |
| **POST request (green)** | Request succeeded! | Error is in response handling code |

### Step 2: Check the Failed Request Details

If you see a failed POST request:

1. **Click on the request**
2. **Go to Headers tab**
3. **Check:**
   - Status Code (should show if backend responded)
   - Request URL (should be `https://dc-intel-api.onrender.com/api/auth/reset-password`)
   - Request Headers (should include `Content-Type: application/json`)

4. **Go to Response tab**
5. **Check:**
   - Is there a response body?
   - Does it contain JSON?
   - What does it say?

### Step 3: Check Console for JavaScript Errors

**Look for errors AFTER clicking "Reset Password":**

```javascript
// Good - shows the request was made
Reset password error: Error: This reset link has expired.

// Bad - shows fetch never completed
TypeError: Failed to fetch
```

If you see `TypeError: Failed to fetch` → network/extension issue

### Step 4: Test in Incognito Mode

1. Open **Incognito/Private window**
2. Navigate to reset password page
3. Try the flow again

**If it works in incognito:**
- Problem is a browser extension
- Disable extensions one by one to find it

**If it still fails in incognito:**
- Problem is network/DNS/firewall
- Try different network (mobile hotspot)

---

## 🛠️ Quick Fixes to Try

### Fix 1: Disable Ad Blocker Temporarily

1. Click ad blocker extension icon
2. Disable it for `datacenterhive.github.io`
3. Reload page and try again

### Fix 2: Whitelist the API Domain

If using uBlock Origin or similar:
1. Click extension icon
2. Click settings/dashboard
3. Add to whitelist: `dc-intel-api.onrender.com`

### Fix 3: Check Browser Security Settings

**Chrome:**
1. Settings → Privacy and security
2. Security → "Standard protection" (not Strict)
3. Clear browsing data → Cached images and files

**Firefox:**
1. Options → Privacy & Security
2. Enhanced Tracking Protection → "Standard"
3. Disable "Strict" mode if enabled

### Fix 4: Try Different Browser

- If you're using Chrome → try Firefox
- If you're using Firefox → try Chrome
- If both fail → likely network/firewall issue

---

## 🧪 Manual Test with curl (Verify Backend Works)

From WSL or terminal:

```bash
# Test with a fake token (should return 400 with "Invalid or expired reset token")
curl -i -X POST https://dc-intel-api.onrender.com/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -H "Origin: https://datacenterhive.github.io" \
  -d '{"token":"test123","new_password":"ValidPass123"}'
```

**Expected result:**
```
HTTP/2 400
access-control-allow-origin: https://datacenterhive.github.io
content-type: application/json

{"detail":"Invalid or expired reset token"}
```

✅ If you get this → backend is working fine
❌ If you get connection error → backend might be down

---

## 📊 Verification Results

### ✅ Backend Status: WORKING

| Test | Result | Status |
|------|--------|--------|
| API reachable | `HTTP/2 400` response | ✅ Working |
| Endpoint exists | Returns JSON error | ✅ Working |
| CORS configured | `access-control-allow-origin` header present | ✅ Working |
| POST allowed | `access-control-allow-methods: POST` | ✅ Working |
| Origin allowed | `https://datacenterhive.github.io` | ✅ Working |

### ❓ Frontend Status: NEEDS USER DEBUGGING

**Since backend works, the issue is on the browser side:**

1. Browser extension blocking request
2. Network connectivity issue
3. DNS resolution problem
4. Firewall blocking Render.com
5. JavaScript error in response handling

**Next step:** Follow the debugging checklist above to identify which one.

---

## 🆘 If Still Not Working

**Copy this information and share it:**

1. **What browser are you using?**
   - Chrome / Firefox / Safari / Edge
   - Version number (Help → About)

2. **What do you see in DevTools Network tab?**
   - Screenshot showing the request list
   - OR description: "No request appears" / "Request is red" / "Request succeeds"

3. **What do you see in DevTools Console tab?**
   - Any error messages
   - Full error text

4. **Does it work in Incognito mode?**
   - Yes / No

5. **Do you have any ad blockers or privacy extensions?**
   - Which ones?

6. **Does this curl command work for you?**
```bash
curl -X POST https://dc-intel-api.onrender.com/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token":"test","new_password":"Test123"}'
```

---

## Summary

✅ **Backend is working correctly**
✅ **CORS is properly configured**
✅ **API endpoint is reachable**
✅ **JavaScript syntax is valid**

❓ **Issue is likely:**
- Browser extension blocking request
- Network/firewall issue on user's side
- JavaScript error in response handling

**Next step:** Follow debugging checklist to identify the specific cause.
