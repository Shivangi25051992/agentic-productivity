#!/usr/bin/env python3
"""
Direct Firestore access to analyze all feedback
"""
import sys
import os

# Set Google Cloud project
os.environ['GOOGLE_CLOUD_PROJECT'] = 'productivityai-mvp'

try:
    from google.cloud import firestore
except ImportError:
    print("Installing google-cloud-firestore...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "google-cloud-firestore", "--break-system-packages", "--quiet"], check=True)
    from google.cloud import firestore

from datetime import datetime

print("="*80)
print("📊 FEEDBACK ANALYSIS - Direct Firestore Access")
print("="*80)
print()

# Initialize Firestore
db = firestore.Client(project='productivityai-mvp')

print("🔍 Fetching all feedback from Firestore...")
feedback_ref = db.collection('feedback')
docs = feedback_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()

all_feedback = []
for doc in docs:
    data = doc.to_dict()
    data['id'] = doc.id
    all_feedback.append(data)

print(f"✅ Found {len(all_feedback)} feedback submissions\n")

# Statistics
bugs = [f for f in all_feedback if f.get('type') == 'bug']
suggestions = [f for f in all_feedback if f.get('type') == 'suggestion']
questions = [f for f in all_feedback if f.get('type') == 'question']
praise = [f for f in all_feedback if f.get('type') == 'praise']
with_screenshots = [f for f in all_feedback if f.get('has_screenshot')]

print("="*80)
print("📊 STATISTICS")
print("="*80)
print(f"Total Feedback: {len(all_feedback)}")
print(f"🐛 Bugs: {len(bugs)}")
print(f"💡 Suggestions: {len(suggestions)}")
print(f"❓ Questions: {len(questions)}")
print(f"👍 Praise: {len(praise)}")
print(f"📷 With Screenshots: {len(with_screenshots)}")
print()

# Display all feedback
print("="*80)
print("📝 ALL FEEDBACK (Most Recent First)")
print("="*80)
print()

for idx, fb in enumerate(all_feedback, 1):
    timestamp = fb.get('timestamp')
    if isinstance(timestamp, datetime):
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    else:
        timestamp_str = str(timestamp)
    
    print(f"{'='*80}")
    print(f"FEEDBACK #{idx}")
    print(f"{'='*80}")
    print(f"ID: {fb.get('id', 'N/A')}")
    print(f"Type: {fb.get('type', 'N/A').upper()}")
    print(f"User: {fb.get('user_email', 'N/A')}")
    print(f"Screen: {fb.get('screen', 'N/A')}")
    print(f"Timestamp: {timestamp_str}")
    print()
    print(f"📷 Screenshots:")
    print(f"  Has Screenshots: {fb.get('has_screenshot', False)}")
    print(f"  Count: {fb.get('screenshot_count', 0)}")
    if fb.get('screenshot_size'):
        size_kb = fb.get('screenshot_size', 0) / 1024
        print(f"  Total Size: {size_kb:.2f} KB")
    print()
    print("💬 COMMENT:")
    print("-"*80)
    comment = fb.get('comment', 'N/A')
    print(comment)
    print("-"*80)
    print()

# Actionable items
print()
print("="*80)
print("🔧 ACTIONABLE ITEMS (Bugs + Suggestions)")
print("="*80)
print()

actionable = bugs + suggestions

for idx, issue in enumerate(actionable, 1):
    emoji = "🐛" if issue.get("type") == "bug" else "💡"
    
    print(f"{idx}. {emoji} [{issue.get('type', '').upper()}]")
    print(f"   Screen: {issue.get('screen', 'N/A')}")
    print(f"   User: {issue.get('user_email', 'N/A')}")
    
    comment = issue.get('comment', 'N/A')
    # Show full comment for analysis
    print(f"   Comment:")
    for line in comment.split('\n'):
        print(f"     {line}")
    
    if issue.get('has_screenshot'):
        count = issue.get('screenshot_count', 0)
        size = issue.get('screenshot_size', 0) / 1024
        print(f"   📷 {count} screenshot(s) - Total: {size:.2f} KB")
    print()

# Summary
print()
print("="*80)
print("📋 SUMMARY FOR DEVELOPER")
print("="*80)
print(f"Total Feedback: {len(all_feedback)}")
print(f"Actionable Items: {len(actionable)}")
print(f"  - Bugs: {len(bugs)}")
print(f"  - Suggestions: {len(suggestions)}")
print(f"With Screenshots: {len(with_screenshots)}")
print()

if actionable:
    print("🎯 NEXT STEPS:")
    print("1. Review each actionable item above")
    print("2. Identify root causes")
    print("3. Create fixes")
    print("4. Test and deploy")
else:
    print("✅ No actionable items - all feedback is praise or questions!")

print()
print("="*80)

