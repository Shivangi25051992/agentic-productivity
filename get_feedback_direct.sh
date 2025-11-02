#!/bin/bash
# Direct Firestore access via gcloud CLI

echo "=========================================="
echo "📊 Fetching ALL Feedback from Firestore"
echo "=========================================="
echo ""

# Use gcloud to query Firestore
/Users/pchintanwar/google-cloud-sdk/bin/gcloud firestore documents list \
  --project=productivityai-mvp \
  --collection-ids=feedback \
  --format=json > feedback_raw.json

echo "✅ Fetched feedback data"
echo ""

# Parse and display
python3 << 'PYTHON'
import json
import sys
from datetime import datetime

try:
    with open('feedback_raw.json', 'r') as f:
        docs = json.load(f)
except:
    print("❌ No feedback found or error reading file")
    sys.exit(1)

print("="*80)
print(f"📊 TOTAL FEEDBACK: {len(docs)}")
print("="*80)
print()

all_feedback = []

for doc in docs:
    fields = doc.get('fields', {})
    
    # Extract fields
    feedback = {
        'id': doc.get('name', '').split('/')[-1],
        'type': fields.get('type', {}).get('stringValue', 'N/A'),
        'comment': fields.get('comment', {}).get('stringValue', 'N/A'),
        'user_email': fields.get('user_email', {}).get('stringValue', 'N/A'),
        'screen': fields.get('screen', {}).get('stringValue', 'N/A'),
        'has_screenshot': fields.get('has_screenshot', {}).get('booleanValue', False),
        'screenshot_count': fields.get('screenshot_count', {}).get('integerValue', 0),
        'status': fields.get('status', {}).get('stringValue', 'new'),
    }
    
    # Get timestamp
    timestamp = fields.get('timestamp', {}).get('timestampValue') or fields.get('created_at', {}).get('timestampValue')
    feedback['timestamp'] = timestamp if timestamp else 'N/A'
    
    all_feedback.append(feedback)

# Sort by most recent
all_feedback.sort(key=lambda x: x['timestamp'], reverse=True)

# Display all
for idx, fb in enumerate(all_feedback, 1):
    print(f"{'='*80}")
    print(f"FEEDBACK #{idx}")
    print(f"{'='*80}")
    print(f"ID: {fb['id']}")
    print(f"Type: {fb['type'].upper()}")
    print(f"Status: {fb['status'].upper()}")
    print(f"User: {fb['user_email']}")
    print(f"Screen: {fb['screen']}")
    print(f"Timestamp: {fb['timestamp']}")
    print(f"Has Screenshots: {fb['has_screenshot']}")
    print(f"Screenshot Count: {fb['screenshot_count']}")
    print()
    print("💬 COMMENT:")
    print("-"*80)
    print(fb['comment'])
    print("-"*80)
    print()

# Save to JSON for AI analysis
with open('feedback_for_analysis.json', 'w') as f:
    json.dump(all_feedback, f, indent=2)

print()
print("="*80)
print("✅ Feedback saved to feedback_for_analysis.json")
print("="*80)

PYTHON

