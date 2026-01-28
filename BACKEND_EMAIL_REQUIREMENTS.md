# Backend Email Notification Requirements

## Overview
The account settings page now calls `PATCH /api/auth/profile` when users update their profile. The backend needs to send email notifications whenever profile changes occur.

## Required Backend Changes

### 1. PATCH /api/auth/profile Endpoint
**Current Status**: Needs to be implemented or verified

**Request:**
```json
PATCH /api/auth/profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "John Doe",
  "company": "Acme Corp",
  "job_title": "CTO"
}
```

**Response:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "company": "Acme Corp",
  "job_title": "CTO",
  "tier": "premium",
  "subscription_status": "active",
  "cancel_at_period_end": false,
  "subscription_end_date": "2026-02-27T00:00:00Z"
}
```

### 2. Email Notification When Profile is Updated

**Trigger**: Whenever `PATCH /api/auth/profile` is called successfully

**Email Template** (profile_updated.html):
```
Subject: Profile Updated - DataCenter Hive

Hi {full_name},

Your DataCenter Hive account profile was just updated on {datetime}.

Changes made:
- Display Name: {old_full_name} → {new_full_name}
- Company: {old_company} → {new_company}
- Job Title: {old_job_title} → {new_job_title}

Request Details:
- Date/Time: {datetime} UTC
- IP Address: {ip_address}
- User Agent: {user_agent}

If you did not make this change, please contact support immediately at support@datacenterhive.com

Best regards,
The DataCenter Hive Team
https://datacenterhive.github.io/dc-intel-site/
```

### 3. Implementation Details

**Python (FastAPI) Example:**
```python
from fastapi import BackgroundTasks
import httpx

@router.patch("/api/auth/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    # Get old values for comparison
    old_data = {
        "full_name": current_user.full_name,
        "company": current_user.company,
        "job_title": current_user.job_title
    }

    # Update user profile in database
    current_user.full_name = profile_data.full_name
    current_user.company = profile_data.company
    current_user.job_title = profile_data.job_title
    db.commit()

    # Queue email notification in background
    background_tasks.add_task(
        send_profile_update_email,
        user=current_user,
        old_data=old_data,
        new_data=profile_data.dict(),
        ip_address=request.client.host if request else "Unknown",
        user_agent=request.headers.get("user-agent", "Unknown") if request else "Unknown"
    )

    return current_user

async def send_profile_update_email(user, old_data, new_data, ip_address, user_agent):
    """Send email notification about profile changes"""

    # Build changes list
    changes = []
    if old_data["full_name"] != new_data["full_name"]:
        changes.append(f"- Display Name: {old_data['full_name']} → {new_data['full_name']}")
    if old_data["company"] != new_data["company"]:
        changes.append(f"- Company: {old_data['company']} → {new_data['company']}")
    if old_data["job_title"] != new_data["job_title"]:
        changes.append(f"- Job Title: {old_data['job_title']} → {new_data['job_title']}")

    if not changes:
        return  # No changes to notify about

    changes_text = "\n".join(changes)

    # Send email via your email service (SendGrid, SES, etc.)
    await send_email(
        to=user.email,
        subject="Profile Updated - DataCenter Hive",
        template="profile_updated",
        context={
            "full_name": user.full_name,
            "changes": changes_text,
            "datetime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "ip_address": ip_address,
            "user_agent": user_agent
        }
    )
```

### 4. Additional Email Notifications to Implement

#### a. Password Changed
**Trigger**: When user changes password
**Template**: password_changed.html

#### b. Subscription Upgraded
**Trigger**: When subscription tier changes
**Template**: subscription_upgraded.html

#### c. Subscription Downgraded/Canceled
**Trigger**: When subscription is canceled or downgraded
**Template**: subscription_canceled.html

#### d. Payment Failed
**Trigger**: When subscription payment fails (past_due status)
**Template**: payment_failed.html

#### e. Trial Ending Soon
**Trigger**: 3 days before trial ends
**Template**: trial_ending.html

### 5. Security Considerations

1. **Rate Limiting**: Limit profile updates to prevent abuse (e.g., max 10 updates per hour)
2. **Validation**: Validate all profile fields (no XSS, SQL injection)
3. **Audit Logging**: Log all profile changes to database audit table
4. **IP Tracking**: Store IP address and user agent for security monitoring
5. **Email Verification**: Consider requiring email verification for sensitive changes

### 6. Database Schema Addition

Add audit log table:
```sql
CREATE TABLE user_profile_changes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7. Testing Checklist

- [ ] `PATCH /api/auth/profile` endpoint exists and works
- [ ] Email is sent when profile is updated
- [ ] Email contains accurate change details
- [ ] Email is NOT sent if no changes are made
- [ ] Rate limiting works (reject too many updates)
- [ ] Audit log is created for each change
- [ ] Invalid data is rejected (validation works)
- [ ] Unauthorized requests return 401
- [ ] Email template renders correctly in major email clients

---

## Password Reset Flow

### 1. POST /api/auth/forgot-password

**Purpose**: Initiate password reset process

**Request:**
```json
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
HTTP 200 OK (always, don't leak email existence)

{
  "message": "If an account exists with that email, we've sent password reset instructions."
}
```

**Backend Implementation:**
```python
@router.post("/api/auth/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    email = data.email.lower().strip()

    # Rate limiting: max 3 requests per email per hour
    # Rate limiting: max 10 requests per IP per hour

    # Check if user exists (don't leak this in response)
    user = db.query(User).filter(User.email == email).first()

    if user:
        # Generate secure token (use secrets.token_urlsafe(32))
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Store hashed token with expiry (15 minutes)
        expires_at = datetime.utcnow() + timedelta(minutes=15)

        # Save to database
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False
        )
        db.add(reset_token)
        db.commit()

        # Send email with reset link
        # ⚠️ CRITICAL: Must include /dc-intel-site/ base path for GitHub Pages
        # ⚠️ CRITICAL: Must URL-encode the token
        from urllib.parse import quote
        FRONTEND_BASE_URL = "https://datacenterhive.github.io/dc-intel-site"  # No trailing slash
        reset_link = f"{FRONTEND_BASE_URL}/auth/reset-password.html?token={quote(token)}"

        # Example result:
        # https://datacenterhive.github.io/dc-intel-site/auth/reset-password.html?token=abc123xyz

        background_tasks.add_task(
            send_password_reset_email,
            to=user.email,
            reset_link=reset_link,
            expires_minutes=15
        )

    # Always return success (security best practice)
    return {"message": "If an account exists with that email, we've sent password reset instructions."}
```

**Email Template:**
```
Subject: Password Reset Request - DataCenter Hive

Hi {full_name},

We received a request to reset your password for DataCenter Hive.

Click the link below to reset your password:
{reset_link}

This link will expire in 15 minutes.

If you didn't request this, please ignore this email. Your password will remain unchanged.

Request Details:
- Date/Time: {datetime} UTC
- IP Address: {ip_address}

Best regards,
The DataCenter Hive Team
```

---

### 2. POST /api/auth/reset-password

**Purpose**: Complete password reset with token

**Request:**
```json
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "abc123...",
  "new_password": "NewSecureP@ss123"
}
```

**Response (Success):**
```json
HTTP 200 OK

{
  "message": "Password has been reset successfully"
}
```

**Response (Error):**
```json
HTTP 400 Bad Request

{
  "detail": "Reset token has expired"
}
```

**Backend Implementation:**
```python
@router.post("/api/auth/reset-password")
async def reset_password(data: ResetPasswordRequest, background_tasks: BackgroundTasks, request: Request):
    token = data.token
    new_password = data.new_password

    # Hash the token to find it
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    # Find token in database
    reset_token = db.query(PasswordResetToken)\
        .filter(PasswordResetToken.token_hash == token_hash)\
        .filter(PasswordResetToken.used == False)\
        .first()

    if not reset_token:
        raise HTTPException(status_code=404, detail="Invalid reset token")

    # Check if expired
    if datetime.utcnow() > reset_token.expires_at:
        raise HTTPException(status_code=400, detail="Reset token has expired")

    # Check if already used
    if reset_token.used:
        raise HTTPException(status_code=400, detail="Reset token has already been used")

    # Validate password strength
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.isupper() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must include uppercase letter")
    if not any(c.isdigit() for c in new_password):
        raise HTTPException(status_code=400, detail="Password must include a number")

    # Get user
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update password (hash it properly with bcrypt/argon2)
    user.password_hash = hash_password(new_password)

    # Mark token as used
    reset_token.used = True
    reset_token.used_at = datetime.utcnow()

    db.commit()

    # Send confirmation email
    background_tasks.add_task(
        send_password_changed_email,
        to=user.email,
        ip_address=request.client.host if request else "Unknown",
        datetime=datetime.utcnow()
    )

    return {"message": "Password has been reset successfully"}
```

**Database Schema:**
```sql
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL,  -- SHA256 hash of token
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_token_hash (token_hash),
    INDEX idx_user_expires (user_id, expires_at)
);
```

**Security Requirements:**
1. ✅ Store hashed tokens (SHA256), never plain text
2. ✅ Tokens expire after 15 minutes
3. ✅ One-time use only (mark as `used`)
4. ✅ Rate limiting on forgot-password (3/hour per email, 10/hour per IP)
5. ✅ Always return generic success message (no email enumeration)
6. ✅ Delete or mark old tokens as expired (cleanup job)
7. ✅ Send confirmation email after password change

---

### 🐛 Troubleshooting Common Issues

#### Issue: "Reset link just takes me back to the website"

**Cause #1:** Email link is missing `/dc-intel-site/` base path

❌ **Wrong:**
```
https://datacenterhive.github.io/auth/reset-password.html?token=abc123
```

✅ **Correct:**
```
https://datacenterhive.github.io/dc-intel-site/auth/reset-password.html?token=abc123
```

**Fix:** Use the `FRONTEND_BASE_URL` constant shown in the code above.

**Cause #2:** Token is not URL-encoded

Some tokens contain special characters that break URLs (`+`, `/`, `=`). Always use `urllib.parse.quote()` (Python) or `encodeURIComponent()` (JavaScript).

**Cause #3:** Email client stripped the token

Some email security systems rewrite links and strip query parameters. The improved frontend now shows a detailed error message explaining what went wrong.

#### Issue: "Token expired" error immediately

**Cause:** Server time is wrong or token was created long ago

**Fix:**
- Ensure server uses UTC time
- Set reasonable expiry (15-60 minutes)
- Check token `created_at` vs `expires_at` in database

#### Issue: "Token already used" error

**Cause:** User clicked the link twice

**Fix:** This is working as intended (security). User should request a new reset link.

---

### 📧 Email Template Example

**Subject:** Password Reset Request - DataCenter Hive

**Body:**
```html
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2>Password Reset Request</h2>

    <p>Hi {full_name},</p>

    <p>We received a request to reset your password for DataCenter Hive.</p>

    <p>Click the button below to reset your password:</p>

    <p style="text-align: center; margin: 30px 0;">
        <a href="{reset_link}"
           style="background: #2563eb;
                  color: white;
                  padding: 12px 24px;
                  text-decoration: none;
                  border-radius: 6px;
                  display: inline-block;">
            Reset Password
        </a>
    </p>

    <p style="font-size: 12px; color: #666;">
        Or copy and paste this link into your browser:<br>
        <a href="{reset_link}">{reset_link}</a>
    </p>

    <p><strong>This link will expire in 15 minutes.</strong></p>

    <p>If you didn't request this, please ignore this email. Your password will remain unchanged.</p>

    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">

    <p style="font-size: 12px; color: #666;">
        <strong>Request Details:</strong><br>
        Date/Time: {datetime} UTC<br>
        IP Address: {ip_address}
    </p>

    <p style="font-size: 12px; color: #666;">
        Best regards,<br>
        The DataCenter Hive Team<br>
        <a href="https://datacenterhive.github.io/dc-intel-site/">datacenterhive.github.io/dc-intel-site</a>
    </p>
</body>
</html>
```

**⚠️ CRITICAL:** The `{reset_link}` must be the FULL URL including:
- Protocol: `https://`
- Domain: `datacenterhive.github.io`
- Base path: `/dc-intel-site`
- Page: `/auth/reset-password.html`
- Token parameter: `?token={url_encoded_token}`

**🚨 CRITICAL: Disable Link Tracking for Security**

Many email services (SendGrid, Mailchimp, etc.) wrap links in tracking redirects:
```
❌ http://url2349.datacenterhive.com/ls/click?upn=...encoded...
```

This BREAKS password reset links! **You MUST disable click tracking for security emails.**

**SendGrid Example:**
```python
from sendgrid.helpers.mail import Mail, TrackingSettings, ClickTracking

message = Mail(
    from_email='noreply@datacenterhive.com',
    to_emails=user.email,
    subject='Password Reset Request',
    html_content=email_html
)

# Disable click tracking (CRITICAL for security emails)
tracking = TrackingSettings()
tracking.click_tracking = ClickTracking(enable=False, enable_text=False)
message.tracking_settings = tracking

sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
response = sg.send(message)
```

**Why disable tracking?**
1. Security: Tracking redirects can leak reset tokens in server logs
2. Reliability: Tracking domains can be misconfigured or blocked
3. Privacy: Password resets shouldn't be tracked
4. Performance: Direct links are faster

**Alternative:** Include both a button AND plain text link:
```html
<p style="text-align: center;">
    <a href="{reset_link}" style="...">Reset Password</a>
</p>

<p style="font-size: 12px;">
    <strong>Link not working?</strong> Copy this URL:<br>
    <code>{reset_link}</code>
</p>
```

---

## Current Status

**Frontend**: ✅ Complete
- Account settings page calls `PATCH /api/auth/profile`
- Forgot password page: `/auth/forgot-password.html`
- Reset password page: `/auth/reset-password.html`
- Change Password button redirects to forgot password flow

**Backend**: ⚠️  Requires Implementation
- Add `PATCH /api/auth/profile` endpoint (if not exists)
- Add `POST /api/auth/forgot-password` endpoint
- Add `POST /api/auth/reset-password` endpoint
- Add `password_reset_tokens` table
- Add email notification on profile update
- Add password reset email templates
- Add audit logging
- Add rate limiting

## Next Steps

1. Verify if `PATCH /api/auth/profile` endpoint already exists in main.py
2. If not, implement the endpoint
3. Integrate email service (SendGrid, AWS SES, or similar)
4. Create email templates
5. Add background task for sending emails
6. Add audit logging table and logic
7. Test thoroughly
8. Deploy to production

## Contact
For questions about implementation, contact the backend developer or create an issue in the dc-intel-api repository.
