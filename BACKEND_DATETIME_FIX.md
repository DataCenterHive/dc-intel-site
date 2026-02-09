# Backend DateTime Comparison Bug - FIXED

## The Error (500 Internal Server Error)

```python
File "/opt/render/project/src/database_postgres.py", line 473, in verify_reset_token
    if datetime.now(timezone.utc) > row['expires_at']:
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: can't compare offset-naive and offset-aware datetimes
```

**Impact:** Password reset completely broken - returns 500 error

---

## Root Cause

**File:** `database_postgres.py`
**Line:** 473
**Function:** `verify_reset_token()`

### The Bug:

```python
if datetime.now(timezone.utc) > row['expires_at']:
```

**Problem:**
- `datetime.now(timezone.utc)` → **timezone-AWARE** (has UTC timezone info)
- `row['expires_at']` → **timezone-NAIVE** (no timezone info)
- Python **refuses** to compare these

### Why This Happens:

Your PostgreSQL database likely stores `expires_at` as:
```sql
expires_at TIMESTAMP  -- Without time zone (naive)
```

Instead of:
```sql
expires_at TIMESTAMP WITH TIME ZONE  -- With time zone (aware)
```

When you query the database, PostgreSQL returns a naive datetime, but your code tries to compare it with an aware datetime.

---

## The Fix

### Quick Fix (database_postgres.py line 473)

**Before (Broken):**
```python
def verify_reset_token(token: str):
    # ... query database for token ...

    # Line 473 - CRASHES HERE
    if datetime.now(timezone.utc) > row['expires_at']:
        return None  # Token expired

    return row
```

**After (Fixed):**
```python
from datetime import datetime, timezone

def verify_reset_token(token: str):
    # ... query database for token ...

    # Get expires_at from database
    expires_at = row['expires_at']

    # Make it timezone-aware if it's naive
    if expires_at.tzinfo is None:
        # Database stores UTC times without timezone info
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    # Now both are aware - comparison works!
    if datetime.now(timezone.utc) > expires_at:
        return None  # Token expired

    return row
```

### Better Fix: Helper Function

Create a helper function and use it everywhere:

```python
from datetime import datetime, timezone

def make_aware(dt):
    """
    Convert naive datetime to UTC-aware datetime.
    If already aware, return as-is.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume naive datetimes from database are UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt

def verify_reset_token(token: str):
    # ... query database ...

    expires_at = make_aware(row['expires_at'])

    if datetime.now(timezone.utc) > expires_at:
        return None

    return row
```

### Best Fix: Fix Database Schema

**Option A: Change Column Type (Recommended)**

```sql
-- Make expires_at timezone-aware
ALTER TABLE password_reset_tokens
ALTER COLUMN expires_at TYPE TIMESTAMP WITH TIME ZONE
USING expires_at AT TIME ZONE 'UTC';

-- Do the same for all datetime columns
ALTER TABLE password_reset_tokens
ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
USING created_at AT TIME ZONE 'UTC';

ALTER TABLE password_reset_tokens
ALTER COLUMN used_at TYPE TIMESTAMP WITH TIME ZONE
USING used_at AT TIME ZONE 'UTC';
```

**Option B: Update Insert/Update Statements**

When creating tokens, ensure you save timezone-aware datetimes:

```python
from datetime import datetime, timezone, timedelta

# CORRECT - timezone-aware
expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

# Save to database
db.execute(
    "INSERT INTO password_reset_tokens (token_hash, expires_at, ...) VALUES (%s, %s, ...)",
    (token_hash, expires_at, ...)
)
```

---

## Where Else This Might Be Broken

Search your codebase for similar comparisons:

```bash
# Find all datetime comparisons
grep -rn "datetime.now(timezone.utc)" src/
grep -rn "datetime.utcnow()" src/
grep -rn "> row\[" src/ | grep -i "date"
grep -rn "< row\[" src/ | grep -i "date"
```

**Common places to check:**

1. **Token expiry checks:**
   ```python
   if datetime.now(timezone.utc) > row['expires_at']:  # FIX THIS
   ```

2. **Session expiry checks:**
   ```python
   if datetime.now(timezone.utc) > session['expires_at']:  # FIX THIS
   ```

3. **Subscription end date checks:**
   ```python
   if datetime.now(timezone.utc) > user['subscription_end_date']:  # FIX THIS
   ```

4. **Created/updated timestamp comparisons:**
   ```python
   if datetime.now(timezone.utc) - row['created_at'] > timedelta(days=7):  # FIX THIS
   ```

**Apply the same fix everywhere:**
```python
# Always make database datetimes aware before comparing
value = make_aware(row['some_date_column'])
if datetime.now(timezone.utc) > value:
    # ... do something
```

---

## Testing the Fix

### 1. Local Test

```python
# test_datetime_fix.py
from datetime import datetime, timezone, timedelta

def make_aware(dt):
    """Convert naive datetime to UTC-aware"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

# Simulate database returning naive datetime
db_expires_at = datetime.utcnow() + timedelta(minutes=15)  # Naive datetime
print(f"Database value: {db_expires_at}")
print(f"Timezone info: {db_expires_at.tzinfo}")  # Should print: None

# Make it aware
expires_at = make_aware(db_expires_at)
print(f"Made aware: {expires_at}")
print(f"Timezone info: {expires_at.tzinfo}")  # Should print: UTC

# Compare (should work now)
now = datetime.now(timezone.utc)
print(f"Current time: {now}")

if now > expires_at:
    print("✓ Comparison works! Token is expired.")
else:
    print("✓ Comparison works! Token is still valid.")
```

Run this:
```bash
python test_datetime_fix.py
```

**Expected output:**
```
Database value: 2026-01-28 02:08:46.123456
Timezone info: None
Made aware: 2026-01-28 02:08:46.123456+00:00
Timezone info: UTC
Current time: 2026-01-28 01:53:46.654321+00:00
✓ Comparison works! Token is still valid.
```

### 2. Deploy and Test

After fixing the code:

```bash
cd /opt/render/project/src
git add database_postgres.py
git commit -m "Fix timezone comparison in verify_reset_token"
git push origin main
```

Render will auto-deploy (watch logs for confirmation).

### 3. Test with curl

```bash
curl -i -X POST https://dc-intel-api.onrender.com/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -H "Origin: https://datacenterhive.github.io" \
  -d '{
    "token": "4q22_tft1G6X_SJKmjFdbRqxRryhMAMnCKZDb1Jt6gw",
    "new_password": "NewValidPass123"
  }'
```

**Expected results:**

**If token is valid and not expired:**
```
HTTP/2 200 OK
access-control-allow-origin: https://datacenterhive.github.io

{"message":"Password has been reset successfully"}
```

**If token has expired:**
```
HTTP/2 400 Bad Request
access-control-allow-origin: https://datacenterhive.github.io

{"detail":"Reset token has expired"}
```

**If token was already used:**
```
HTTP/2 400 Bad Request
access-control-allow-origin: https://datacenterhive.github.io

{"detail":"Reset token has already been used"}
```

**Should NOT see:**
```
HTTP/2 500 Internal Server Error  ❌
```

### 4. Test from Browser

1. Request a fresh password reset
2. Click the link in email
3. Enter new password (2x)
4. Click "Reset Password"
5. **Should see success screen!**

---

## Python DateTime Best Practices

### Always Use Timezone-Aware Datetimes

**Good:**
```python
from datetime import datetime, timezone, timedelta

# Current time (aware)
now = datetime.now(timezone.utc)

# Future time (aware)
expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

# Save to database
db.execute("INSERT INTO ... VALUES (%s)", (expires_at,))
```

**Bad:**
```python
# ❌ Naive datetime
now = datetime.now()  # No timezone info!

# ❌ Deprecated in Python 3.12+
now = datetime.utcnow()  # Returns naive datetime
```

### Always Make Database Values Aware

```python
def make_aware(dt):
    """Convert naive datetime to UTC-aware datetime"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

# Use it on all database datetimes
user = db.query(...).first()
created_at = make_aware(user.created_at)
updated_at = make_aware(user.updated_at)
```

### Store UTC in Database

**Database schema should use:**
```sql
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
expires_at TIMESTAMP WITH TIME ZONE
```

**NOT:**
```sql
created_at TIMESTAMP DEFAULT NOW()  ❌ Missing timezone
```

---

## Summary

**Error:** `TypeError: can't compare offset-naive and offset-aware datetimes`

**Location:** `database_postgres.py` line 473

**Fix:** Make both datetimes timezone-aware before comparing:
```python
expires_at = row['expires_at']
if expires_at.tzinfo is None:
    expires_at = expires_at.replace(tzinfo=timezone.utc)
if datetime.now(timezone.utc) > expires_at:
    # ...
```

**Impact:** Password reset will work after this fix!

**Prevention:**
- Always use timezone-aware datetimes
- Use `TIMESTAMP WITH TIME ZONE` in PostgreSQL
- Create helper function `make_aware()` for database values

---

## Related Issues to Check

After fixing this, check if you have the same bug in:

- [ ] JWT token expiry checks
- [ ] Session expiry checks
- [ ] Subscription end date checks
- [ ] API key expiry checks
- [ ] Rate limiting timestamp comparisons
- [ ] Created/updated timestamp comparisons

Apply the same fix everywhere!
