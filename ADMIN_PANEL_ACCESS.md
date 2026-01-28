# Admin Panel - Complete Access Guide

## 🎯 Quick Access

**Admin Panel URL**: https://dc-intel-api.onrender.com/admin

**Your Credentials**:
- Email: `yasuleman@gmail.com`
- Password: (your account password)

---

## 📋 What You Can Do

### ✅ Dashboard
- View total users
- See active vs inactive counts
- Monitor admin and enterprise tier users

### ✅ User Management
- **Search**: Find users by email, name, or company
- **Filter by Tier**: free, basic, premium, enterprise
- **Filter by Role**: user, support, admin
- **Filter by Status**: active, inactive
- **Pagination**: Browse through large user lists

### ✅ Edit User
Click "Edit" on any user to:
- **Change Tier**: Upgrade/downgrade subscription tier
- **Change Role**: Promote to admin/support or demote to user
- **Add Reason**: Document why you made the change
- All changes are logged in the audit log

### ✅ Enable/Disable Users
- **Disable**: Block user from logging in (account still exists)
- **Enable**: Restore access to previously disabled user
- Useful for:
  - Temporarily suspending accounts
  - Blocking malicious users
  - Testing subscription flows

### ✅ Audit Log
- See all admin actions
- Tracks: who, what, when, why
- Sortable and filterable
- Full accountability trail

---

## 🔐 Features NOT Available (Yet)

### ❌ Password Reset
The admin panel **cannot reset user passwords** directly.

**Current workarounds:**
1. Use the password reset email flow (user requests reset)
2. Use SQL to manually update password hash
3. Use the `admin_reset_password.py` script

**I can add this feature** - see "Adding Password Reset" section below.

### ❌ Delete Users
The admin panel **cannot delete users** directly (safety feature).

**To delete a user**, you need to use the API directly:
```bash
DELETE /api/admin/users/{email}
```

Or disable the account instead (safer).

---

## 🚀 Using the Admin Panel

### Step 1: Access the Panel

1. Go to: https://dc-intel-api.onrender.com/admin
2. You'll see a login form
3. Enter your email: `yasuleman@gmail.com`
4. Enter your password
5. Click "Login"

### Step 2: View Dashboard

After login, you'll see:
- **Statistics** at the top (total users, active, admins, etc.)
- **User table** with all users
- **Filters** above the table
- **Audit log** tab at the bottom

### Step 3: Manage a User

**To change user tier:**
1. Find the user (search or scroll)
2. Click "Edit" button
3. Select new tier from dropdown
4. Enter reason: "Upgraded for testing"
5. Click "Save"
6. User tier updated immediately

**To disable a user:**
1. Find the user
2. Click "Disable" button
3. Confirm the action
4. User cannot log in anymore
5. Check audit log for entry

**To enable a disabled user:**
1. Find the disabled user (filter by Status: inactive)
2. Click "Enable" button
3. User can now log in again

### Step 4: View Audit Logs

1. Scroll to "Audit Logs" section
2. See all recent admin actions
3. Each entry shows:
   - When (timestamp)
   - Who (admin email)
   - What (action type)
   - Target (affected user)
   - Why (reason)

---

## 🔧 Backend API Endpoints

If you prefer using API calls directly:

### List Users
```bash
curl https://dc-intel-api.onrender.com/api/admin/users \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Get User Details
```bash
curl https://dc-intel-api.onrender.com/api/admin/users/user@example.com \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Change User Tier
```bash
curl -X PATCH https://dc-intel-api.onrender.com/api/admin/users/user@example.com/tier \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_tier": "premium", "reason": "Upgraded"}'
```

### Change User Role
```bash
curl -X PATCH https://dc-intel-api.onrender.com/api/admin/users/user@example.com/role \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_role": "admin", "reason": "Promoted to admin"}'
```

### Disable User
```bash
curl -X PATCH https://dc-intel-api.onrender.com/api/admin/users/user@example.com/disable \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"reason": "Suspicious activity"}'
```

### Enable User
```bash
curl -X PATCH https://dc-intel-api.onrender.com/api/admin/users/user@example.com/enable \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Audit Logs
```bash
curl https://dc-intel-api.onrender.com/api/admin/audit?limit=50 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Stats
```bash
curl https://dc-intel-api.onrender.com/api/admin/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔑 Getting Your JWT Token

If you need your JWT token for API calls:

1. Log into admin panel
2. Open browser DevTools (F12)
3. Go to Console tab
4. Type: `localStorage.getItem('admin_token')`
5. Copy the token value
6. Use it in the `Authorization: Bearer <token>` header

OR

Login via API:
```bash
curl -X POST https://dc-intel-api.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "yasuleman@gmail.com", "password": "your_password"}'
```

Response includes `access_token` field.

---

## 🛡️ Security Features

### Role-Based Access Control (RBAC)
- **admin**: Full access to everything
- **support**: Read-only access (future feature)
- **user**: No admin access

### Last-Admin Protection
- Cannot remove admin role from the last remaining admin
- Prevents locking yourself out

### Self-Demotion Prevention
- Cannot demote your own account
- Must use another admin account

### Break-Glass Access
Emergency admin access via `X-Admin-Key` header:
```bash
curl https://dc-intel-api.onrender.com/api/admin/stats \
  -H "X-Admin-Key: YOUR_ADMIN_KEY"
```

### Comprehensive Audit Logging
- Every admin action is logged
- Immutable audit trail
- Includes: who, what, when, why, IP, user agent

---

## 🐛 Troubleshooting

### Can't Log In
**Problem**: "Incorrect email or password"

**Solutions:**
1. Verify email is exactly: `yasuleman@gmail.com` (lowercase)
2. Check password is correct
3. Verify account is active (check database)
4. Check Render logs for errors

### Not Seeing Admin Panel
**Problem**: 404 Not Found

**Solutions:**
1. Verify URL: `https://dc-intel-api.onrender.com/admin`
2. Check if backend is deployed
3. Check Render logs for errors

### API Endpoints Return 403 Forbidden
**Problem**: "Not authorized"

**Solutions:**
1. Verify your account has `role = admin`
2. Check JWT token is valid
3. Re-login to get fresh token

### Changes Not Saving
**Problem**: Edit modal shows success but changes don't persist

**Solutions:**
1. Check browser Console (F12) for errors
2. Verify backend is responding
3. Check audit logs to see if action was recorded
4. Refresh the page and check if changes persisted

---

## ➕ Adding Password Reset Feature

### What You Need

I can add a "Reset Password" button to the admin panel that:
1. Generates a random secure password
2. Updates the user's password hash
3. Shows you the new password (write it down!)
4. Logs the action in audit log
5. Optionally sends email to user with new password

### Implementation

Would you like me to:
1. Add backend endpoint: `PATCH /api/admin/users/{email}/reset-password`
2. Add "Reset Password" button to admin panel
3. Show modal with the generated password
4. Add to audit log

This would let you reset ANY user's password directly from the admin panel, including your own!

---

## 📊 Database Access (Alternative)

If the admin panel is not accessible, you can manage users directly via database:

### Connect to PostgreSQL (Render.com)

1. Go to Render dashboard
2. Select your PostgreSQL database
3. Click "Connect" → "Shell"
4. Run SQL commands directly

### Common SQL Commands

**List all users:**
```sql
SELECT email, full_name, tier, role, is_active, created_at
FROM users
ORDER BY created_at DESC
LIMIT 20;
```

**Find your account:**
```sql
SELECT * FROM users WHERE email = 'yasuleman@gmail.com';
```

**Change user tier:**
```sql
UPDATE users
SET tier = 'enterprise',
    updated_at = NOW()
WHERE email = 'user@example.com';
```

**Enable/disable user:**
```sql
-- Disable
UPDATE users
SET is_active = FALSE,
    disabled_at = NOW(),
    disabled_reason = 'Admin action'
WHERE email = 'user@example.com';

-- Enable
UPDATE users
SET is_active = TRUE,
    disabled_at = NULL,
    disabled_reason = NULL
WHERE email = 'user@example.com';
```

**Make someone admin:**
```sql
UPDATE users
SET role = 'admin',
    tier = 'enterprise',
    updated_at = NOW()
WHERE email = 'user@example.com';
```

---

## 📚 Related Documentation

- **ADMIN_SYSTEM_COMPLETE.md** - Full admin system implementation details
- **admin_reset_password.py** - CLI tool for password resets
- **check_and_reset_password.md** - Manual password reset guide

---

## Summary

**Access**: https://dc-intel-api.onrender.com/admin

**Features**:
- ✅ Dashboard with statistics
- ✅ User management (search, filter, edit)
- ✅ Change user tier and role
- ✅ Enable/disable accounts
- ✅ Audit log viewer
- ❌ Password reset (not yet - but I can add it!)

**For Password Reset**: Use `admin_reset_password.py` script or SQL for now, OR let me add the feature to the admin panel!
