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

## Current Status

**Frontend**: ✅ Complete - Account settings page calls `PATCH /api/auth/profile`

**Backend**: ⚠️  Requires Implementation
- Add `PATCH /api/auth/profile` endpoint (if not exists)
- Add email notification on profile update
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
