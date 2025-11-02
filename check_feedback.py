#!/usr/bin/env python3
"""
Check feedback submissions in Firestore
"""
import os
from google.cloud import firestore
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment
load_dotenv()
load_dotenv('.env.local', override=True)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
db = firestore.Client(project=PROJECT_ID)

print("="*80)
print("🔍 CHECKING FEEDBACK SUBMISSIONS")
print("="*80)
print(f"Project: {PROJECT_ID}")
print(f"Collection: feedback")
print("="*80)

# Query all feedback, ordered by timestamp descending
feedback_ref = db.collection('feedback')
feedback_docs = feedback_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50).stream()

feedback_list = []
for doc in feedback_docs:
    data = doc.to_dict()
    data['id'] = doc.id
    feedback_list.append(data)

if not feedback_list:
    print("❌ No feedback found in database")
    print("\nPossible reasons:")
    print("1. Feedback not submitted successfully")
    print("2. Backend error during submission")
    print("3. Wrong collection name")
    exit(1)

print(f"\n✅ Found {len(feedback_list)} feedback submission(s)\n")

# Display summary
for idx, feedback in enumerate(feedback_list, 1):
    print(f"{'='*80}")
    print(f"📝 FEEDBACK #{idx}")
    print(f"{'='*80}")
    print(f"ID: {feedback.get('id', 'N/A')}")
    print(f"Type: {feedback.get('type', 'N/A')}")
    print(f"User: {feedback.get('user_email', 'N/A')}")
    print(f"Screen: {feedback.get('screen', 'N/A')}")
    print(f"Timestamp: {feedback.get('timestamp', 'N/A')}")
    print(f"Has Screenshot: {feedback.get('has_screenshot', False)}")
    if feedback.get('screenshot_size'):
        print(f"Screenshot Size: {feedback.get('screenshot_size')} bytes")
    print(f"\nComment:")
    print(f"{feedback.get('comment', 'N/A')}")
    print()

# Summary by type
print(f"{'='*80}")
print("📊 SUMMARY BY TYPE")
print(f"{'='*80}")
type_counts = {}
for feedback in feedback_list:
    ftype = feedback.get('type', 'unknown')
    type_counts[ftype] = type_counts.get(ftype, 0) + 1

for ftype, count in sorted(type_counts.items()):
    emoji = {'bug': '🐛', 'suggestion': '💡', 'question': '❓', 'praise': '👍'}.get(ftype, '📝')
    print(f"{emoji} {ftype.capitalize()}: {count}")

# Check for screenshots
screenshots = [f for f in feedback_list if f.get('has_screenshot')]
print(f"\n📷 Feedback with screenshots: {len(screenshots)}")

print(f"\n{'='*80}")
print("✅ FEEDBACK CHECK COMPLETE")
print(f"{'='*80}")
