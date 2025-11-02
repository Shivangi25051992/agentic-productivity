#!/usr/bin/env python3
import requests
import json

# Admin credentials
BACKEND_URL = "https://aiproductivity-backend-rhwrraai2a-uc.a.run.app"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

print("="*80)
print("🔐 Logging in as admin...")
print("="*80)
login_response = requests.post(
    f"{BACKEND_URL}/admin/login",
    json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    timeout=10
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["token"]
print("✅ Logged in successfully\n")

# Fetch feedback stats
print("="*80)
print("📊 FEEDBACK STATISTICS")
print("="*80)
stats_response = requests.get(
    f"{BACKEND_URL}/admin/feedback/stats",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10
)

if stats_response.status_code == 200:
    stats = stats_response.json()
    print(f"Total: {stats.get('total', 0)}")
    print(f"🐛 Bugs: {stats.get('bugs', 0)}")
    print(f"💡 Suggestions: {stats.get('suggestions', 0)}")
    print(f"❓ Questions: {stats.get('questions', 0)}")
    print(f"👍 Praise: {stats.get('praise', 0)}")
    print(f"✅ Resolved: {stats.get('resolved', 0)}")
    print(f"⏳ Pending: {stats.get('pending', 0)}")
else:
    print(f"⚠️ Could not fetch stats: {stats_response.status_code}")

print()

# Fetch all feedback
print("="*80)
print("📝 FETCHING ALL FEEDBACK...")
print("="*80)
print()

feedback_response = requests.get(
    f"{BACKEND_URL}/admin/feedback/list?limit=50",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10
)

if feedback_response.status_code != 200:
    print(f"❌ Failed to fetch feedback: {feedback_response.status_code}")
    print(feedback_response.text)
    exit(1)

feedback_data = feedback_response.json()
feedbacks = feedback_data.get("feedback", [])

print(f"✅ Found {len(feedbacks)} feedback submissions\n")

# Display all feedback
for idx, fb in enumerate(feedbacks, 1):
    print("="*80)
    print(f"FEEDBACK #{idx}")
    print("="*80)
    print(f"ID: {fb.get('id', 'N/A')}")
    print(f"Type: {fb.get('type', 'N/A').upper()}")
    print(f"Status: {fb.get('status', 'pending').upper()}")
    print(f"User: {fb.get('user_email', 'N/A')}")
    print(f"Screen: {fb.get('screen', 'N/A')}")
    print(f"Timestamp: {fb.get('timestamp', 'N/A')}")
    print()
    print(f"📷 Screenshots:")
    print(f"  - Has Screenshots: {fb.get('has_screenshot', False)}")
    print(f"  - Count: {fb.get('screenshot_count', 0)}")
    if fb.get('screenshot_size'):
        size_kb = fb.get('screenshot_size', 0) / 1024
        print(f"  - Total Size: {size_kb:.1f} KB")
    print()
    print("💬 COMMENT:")
    print("-"*80)
    print(fb.get('comment', 'N/A'))
    print("-"*80)
    print()

print()
print("="*80)
print("🔍 ACTIONABLE ITEMS (Bugs + Suggestions)")
print("="*80)
print()

actionable = [f for f in feedbacks if f.get('type') in ['bug', 'suggestion']]

for idx, issue in enumerate(actionable, 1):
    emoji = "🐛" if issue.get("type") == "bug" else "💡"
    status_emoji = "✅" if issue.get("status") == "resolved" else "⏳"
    
    print(f"{status_emoji} {idx}. {emoji} [{issue.get('type', '').upper()}]")
    print(f"   Screen: {issue.get('screen', 'N/A')}")
    print(f"   User: {issue.get('user_email', 'N/A')}")
    
    comment = issue.get('comment', 'N/A')
    if len(comment) > 150:
        print(f"   Comment: {comment[:150]}...")
    else:
        print(f"   Comment: {comment}")
    
    if issue.get('has_screenshot'):
        print(f"   📷 {issue.get('screenshot_count', 0)} screenshot(s) - Size: {issue.get('screenshot_size', 0)/1024:.1f} KB")
    print()

print()
print("="*80)
print("📊 SUMMARY")
print("="*80)
print(f"Total Feedback: {len(feedbacks)}")
print(f"Actionable Items: {len(actionable)}")
print(f"With Screenshots: {len([f for f in feedbacks if f.get('has_screenshot')])}")
print()

