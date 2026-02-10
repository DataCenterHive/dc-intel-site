#!/usr/bin/env python3
"""
Final fixes to complete visual overhaul per spec.
Removes all alert() calls and applies remaining requirements.
"""

import re

# Read the file
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Track changes
changes = []

# 1. Replace all alert() calls with showToast() or appropriate modal
alert_patterns = [
    # Watchlist failures
    (r"alert\('Failed to update watchlist\. Please try again\.'\);",
     "showToast('Failed to update watchlist. Please try again.', 'error');"),
    (r"alert\('Failed to remove from watchlist\. Please try again\.'\);",
     "showToast('Failed to remove from watchlist. Please try again.', 'error');"),

    # Export - require login
    (r"alert\('Please create a free account to export data\.'\);",
     "showToast('Please create a free account to export data.', 'info');"),

    # Export success
    (r"alert\(`Export successful! You have \$\{exportsLeft\} export\$\{exportsLeft !== 1 \? 's' : ''\} remaining on your free account\.`\);",
     "showToast(`Export successful! You have ${exportsLeft} export${exportsLeft !== 1 ? 's' : ''} remaining.`, 'success');"),

    # Certification unlock
    (r"alert\('Thank you! Certification data is now unlocked\. Refreshing the table\.\.\.'\);",
     "showToast('Certification data unlocked!', 'success');"),

    # Login errors
    (r"alert\('Invalid password for test account\.'\);",
     "showToast('Invalid password for test account.', 'error');"),
    (r"alert\(error\.detail \|\| 'Login failed\. Please check your credentials\.'\);",
     "showToast(error.detail || 'Login failed. Please check your credentials.', 'error');"),
    (r"alert\('Login failed\. Invalid response from server\.'\);",
     "showToast('Login failed. Invalid response from server.', 'error');"),
    (r"alert\('Login failed\. Backend API not available\. Use test accounts: basic@test\.com, premium@test\.com, or enterprise@test\.com'\);",
     "showToast('Login failed. Use test accounts: basic@test.com, premium@test.com, or enterprise@test.com', 'error');"),

    # Registration
    (r"alert\('Passwords do not match!'\);",
     "showToast('Passwords do not match!', 'error');"),
    (r"alert\('Registration successful! Welcome to DC Intel\.'\);",
     "showToast('Registration successful! Welcome to DC Intel.', 'success');"),
    (r"alert\(data\.error \|\| data\.detail \|\| 'Registration failed\. Please try again\.'\);",
     "showToast(data.error || data.detail || 'Registration failed. Please try again.', 'error');"),
    (r"alert\('Registration failed\. This feature requires server implementation\.'\);",
     "showToast('Registration failed. Server not available.', 'error');"),

    # Logout
    (r"alert\('You have been logged out\.'\);",
     "showToast('You have been logged out.', 'info');"),

    # Password reset
    (r"alert\('If an account exists with that email, a password reset link has been sent\. Please check your inbox\.'\);",
     "showToast('Password reset link sent. Please check your email.', 'success');"),
    (r"alert\(data\.detail \|\| 'Failed to send reset email\. Please try again\.'\);",
     "showToast(data.detail || 'Failed to send reset email.', 'error');"),
    (r"alert\('Failed to send reset email\. Please try again later\.'\);",
     "showToast('Failed to send reset email. Please try again later.', 'error');"),
    (r"alert\('Password successfully reset! You can now log in with your new password\.'\);",
     "showToast('Password successfully reset!', 'success');"),
    (r"alert\(data\.detail \|\| 'Failed to reset password\. The link may have expired\.'\);",
     "showToast(data.detail || 'Password reset failed. Link may have expired.', 'error');"),
    (r"alert\('Failed to reset password\. Please try again\.'\);",
     "showToast('Failed to reset password. Please try again.', 'error');"),

    # Study guide access - use modal for upsell
    (r"alert\('Please log in to access Study Guide content\.\\n\\nClick the Login button in the top-right corner\.'\);",
     "showToast('Please log in to access Study Guide content.', 'info');"),
    (r"alert\(`This content requires a \$\{access\.requiredTier\} subscription\.\\n\\nPlease upgrade your plan to access this content\.`\);",
     "showUpgradeModal('study-guide', access.requiredTier);"),

    # Service requests
    (r"alert\('Thank you! Your request for ' \+ serviceType \+ ' has been submitted\.\\n\\nYou will receive a confirmation email at ' \+ data\.email \+ ' shortly\.\\n\\nOur team will contact you within 24 hours\.'\);",
     "showToast('Request submitted! We will contact you within 24 hours.', 'success');"),
    (r"alert\('Request submitted\. We will contact you shortly at ' \+ data\.email \+ '\.'\);",
     "showToast('Request submitted. We will contact you shortly.', 'success');"),
    (r"alert\('Thank you! Your request for ' \+ serviceType \+ ' has been submitted\.\\n\\nWe will contact you at ' \+ data\.email \+ ' within 24 hours\.'\);",
     "showToast('Request submitted! We will contact you within 24 hours.', 'success');"),

    # Study guide download
    (r"alert\('Thank you! The study guide will open in a new window\.\\n\\nCheck your email for future updates from DataCenter Hive\.'\);",
     "showToast('Study guide opened! Check your email for updates.', 'success');"),

    # Demo request
    (r"alert\('Thank you for your demo request!\\n\\nOur team will reach out to you within 24 hours at ' \+ data\.email \+ ' to schedule your personalized demo\.'\);",
     "showToast('Demo request received! We will contact you within 24 hours.', 'success');"),

    # Generic service interest
    (r"alert\('Thank you for your interest in ' \+ serviceType \+ '! We will contact you shortly at ' \+ data\.email \+ '\.'\);",
     "showToast('Thank you! We will contact you shortly.', 'success');"),

    # Export errors
    (r"alert\('No data available to export\. Please load the data first\.'\);",
     "showToast('No data available. Please load data first.', 'error');"),

    # Search
    (r"alert\('Please enter a search query'\);",
     "showToast('Please enter a search query', 'info');"),
    (r"alert\('Search failed\. Please try again\.'\);",
     "showToast('Search failed. Please try again.', 'error');"),
    (r"alert\('Search Error: ' \+ error\.message \+ '\\n\\nPlease try again or contact support\.'\);",
     "showToast('Search error: ' + error.message, 'error');"),

    # News loading
    (r"alert\('Unable to load news articles\.'\);",
     "showToast('Unable to load news articles.', 'error');"),
    (r"alert\('No news articles available\.'\);",
     "showToast('No news articles available.', 'info');"),
    (r"alert\('Error loading news: ' \+ error\.message\);",
     "showToast('Error loading news: ' + error.message, 'error');"),
    (r"alert\('News Archive is an Enterprise-only feature\.\\n\\nUpgrade to Enterprise tier \(\$2,499/month\) to access the complete historical archive of DC-related news articles\.\\n\\nContact: support@dc-intel\.com'\);",
     "showUpgradeModal('news-archive', 'Enterprise');"),
    (r"alert\('Unable to load news archive\.'\);",
     "showToast('Unable to load news archive.', 'error');"),
    (r"alert\('No archive articles available\.'\);",
     "showToast('No archive articles available.', 'info');"),
    (r"alert\('Error loading news archive: ' \+ error\.message\);",
     "showToast('Error loading news archive: ' + error.message, 'error');"),
]

for pattern, replacement in alert_patterns:
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        changes.append(f"Replaced alert: {pattern[:50]}...")

print(f"Replaced {len([c for c in changes if 'alert' in c.lower()])} alert() patterns")

# 2. Fix body background
content = re.sub(
    r'body \{([^}]*?)background: var\(--bg-secondary\);',
    r'body {\1background: var(--bg-primary);',
    content
)
changes.append("Changed body background to var(--bg-primary)")

# Write the file
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal changes made: {len(changes)}")
for change in changes[:10]:  # Show first 10
    print(f"  - {change}")
if len(changes) > 10:
    print(f"  ... and {len(changes) - 10} more")

print("\n✅ Phase 1 complete: alert() calls replaced, body background fixed")
