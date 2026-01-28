# Password Reset Link Debugging Guide

## 🔍 The Problem

When you click the reset password link in your email, it "just takes you back to the website" instead of showing the reset password form.

---

## ✅ Step-by-Step Debugging

### Step 1: Copy the Link from Email

1. **Don't click the link yet**
2. Right-click the "Reset Password" button/link in the email
3. Select "Copy link address" (or "Copy link")
4. Paste it into Notepad

**What you should see:**
```
https://datacenterhive.github.io/dc-intel-site/auth/reset-password.html?token=SOME_LONG_STRING
```

---

### Step 2: Check for Common Problems

Compare your link to this checklist:

#### ✅ Has the correct domain?
- Should be: `datacenterhive.github.io`
- NOT: `localhost` or `127.0.0.1` or any other domain

#### ✅ Has `/dc-intel-site/` in the path?
- Should be: `https://datacenterhive.github.io/dc-intel-site/auth/...`
- NOT: `https://datacenterhive.github.io/auth/...` ❌ (missing base path)

#### ✅ Has `/auth/reset-password.html`?
- Should end with: `/auth/reset-password.html?token=...`
- NOT: `/auth/login.html` or `/` or anything else

#### ✅ Has `?token=` query parameter?
- Should have: `?token=SOME_LONG_STRING`
- NOT just: `?token=` with nothing after it
- NOT missing the `?token=` part entirely

---

### Step 3: Test the Link

1. Open **Incognito/Private window** in your browser
2. Paste the full link
3. Press Enter

**What should happen:**
- You see the "Create New Password" form
- Two password fields are visible
- Page title says "Reset Password | DataCenter Hive"

**If it doesn't work, check the browser console:**
1. Press F12 to open DevTools
2. Click "Console" tab
3. Look for these messages:
   ```
   Current URL: https://...
   Token found: YES or NO
   Token value: ...
   ```

---

### Step 4: Identify the Issue

#### Issue A: Missing `/dc-intel-site/` base path

**Symptom:** Link looks like:
```
https://datacenterhive.github.io/auth/reset-password.html?token=...
                                    ^ missing /dc-intel-site/
```

**Fix:** Tell your backend developer to update the email template:
```python
# WRONG:
reset_link = f"https://datacenterhive.github.io/auth/reset-password.html?token={token}"

# CORRECT:
FRONTEND_BASE_URL = "https://datacenterhive.github.io/dc-intel-site"
reset_link = f"{FRONTEND_BASE_URL}/auth/reset-password.html?token={token}"
```

---

#### Issue B: Missing token parameter

**Symptom:** Link looks like:
```
https://datacenterhive.github.io/dc-intel-site/auth/reset-password.html
                                                                        ^ no ?token=...
```

**What you'll see:**
- Error banner: "Invalid Reset Link"
- Message: "The reset link is missing the security token"
- Shows the current URL
- Button: "Request New Reset Link"

**Fix:** Backend is not including the token in the email. Check the email template.

---

#### Issue C: Token is there but page redirects anyway

**Symptom:**
- Link has `/dc-intel-site/` ✅
- Link has `?token=...` ✅
- But page still redirects or shows error

**Possible causes:**
1. **Token has special characters that break the URL**
   - Fix: Backend must URL-encode the token
   - Python: `from urllib.parse import quote; reset_link = f"...?token={quote(token)}"`
   - JavaScript: `const resetLink = \`...?token=${encodeURIComponent(token)}\``

2. **Email client rewrote the link**
   - Some corporate email systems strip query parameters
   - Test with Gmail or a personal email to confirm

3. **GitHub Pages is having issues**
   - Try accessing the page directly: https://datacenterhive.github.io/dc-intel-site/auth/reset-password.html
   - If this doesn't load, check if GitHub Pages is deployed

---

### Step 5: Updated Frontend Debugging

I've improved the reset password page to show you EXACTLY what's wrong.

**When you click a bad link now, you'll see:**
- Error banner with detailed explanation
- The actual URL that was loaded
- What might be wrong (missing token, wrong domain, etc.)
- Console logs showing the exact token value
- Button to request a new link

**Console output example:**
```
Current URL: https://datacenterhive.github.io/dc-intel-site/auth/reset-password.html?token=abc123xyz
Token found: YES
Token value: abc123xyz
```

If token is missing:
```
Current URL: https://datacenterhive.github.io/auth/reset-password.html
Token found: NO
Token value: (missing)
```

---

## 🛠️ Backend Fix (For Your Developer)

The backend email template MUST generate this exact format:

```python
from urllib.parse import quote

# Configuration (put this at the top of your file)
FRONTEND_BASE_URL = "https://datacenterhive.github.io/dc-intel-site"  # No trailing slash

# In the forgot-password endpoint:
def send_password_reset_email(user, token):
    # URL-encode the token (handles special characters)
    encoded_token = quote(token)

    # Build the full reset link
    reset_link = f"{FRONTEND_BASE_URL}/auth/reset-password.html?token={encoded_token}"

    # Example result:
    # https://datacenterhive.github.io/dc-intel-site/auth/reset-password.html?token=abc123xyz

    # Send email with reset_link
    send_email(
        to=user.email,
        subject="Password Reset Request",
        html_template="password_reset.html",
        context={"reset_link": reset_link, "full_name": user.full_name}
    )
```

---

## 📧 Email Template Checklist

Your email HTML should have:

```html
<a href="{reset_link}"
   style="background: #2563eb;
          color: white;
          padding: 12px 24px;
          text-decoration: none;
          border-radius: 6px;">
    Reset Password
</a>
```

**Critical:**
- `{reset_link}` must be replaced with the FULL URL (including `https://`, domain, base path, page, and token)
- Don't build the link in the HTML template - build it in Python and pass it as a variable
- Don't forget to URL-encode the token

---

## ✅ Quick Test

To verify the backend is generating correct links:

1. **Request a password reset** (enter your email)
2. **Check the email** (look in inbox + spam)
3. **Right-click the link** → Copy link address
4. **Paste into Notepad** and verify:
   - ✅ Starts with `https://datacenterhive.github.io/dc-intel-site/`
   - ✅ Contains `/auth/reset-password.html`
   - ✅ Has `?token=` with a long random string after it

If all ✅, the link should work!

---

## 🆘 Still Not Working?

**Copy and paste this information:**

1. The full reset link from your email (can redact most of the token)
2. What you see when you click it (screenshot or description)
3. The console log output (F12 → Console tab)

**Example:**
```
Link from email:
https://datacenterhive.github.io/dc-intel-site/auth/reset-password.html?token=abc123...xyz

What I see:
[Describe what happens - blank page, error message, etc.]

Console output:
Current URL: ...
Token found: YES/NO
Token value: ...
```

With this information, we can pinpoint exactly what's wrong!

---

## 📚 Related Documentation

- **Backend requirements:** See `BACKEND_EMAIL_REQUIREMENTS.md`
- **User feedback fixes:** See `USER_FEEDBACK_FIXES.md`
- **Code review:** See `ACCOUNT_SETTINGS_CODE_REVIEW.md`
