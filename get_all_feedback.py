#!/usr/bin/env python3
import os
import sys
from google.cloud import firestore
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PROJECT_ID = "productivityai-mvp"
db = firestore.Client(project=PROJECT_ID)

print("="*80)
print("📝 ALL USER FEEDBACK")
print("="*80)

feedback_ref = db.collection('feedback').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()

feedback_list = []
for doc in feedback_ref:
    data = doc.to_dict()
    data['id'] = doc.id
    feedback_list.append(data)

if not feedback_list:
    print("❌ No feedback found")
    sys.exit(0)

print(f"\n✅ Found {len(feedback_list)} feedback items\n")

# Group by type
bugs = [f for f in feedback_list if f.get('type') == 'bug']
suggestions = [f for f in feedback_list if f.get('type') == 'suggestion']
questions = [f for f in feedback_list if f.get('type') == 'question']
praise = [f for f in feedback_list if f.get('type') == 'praise']

print(f"🐛 BUGS: {len(bugs)}")
for i, bug in enumerate(bugs, 1):
    print(f"\n  Bug #{i}:")
    print(f"  User: {bug.get('user_email', 'N/A')}")
    print(f"  Time: {bug.get('timestamp', 'N/A')}")
    print(f"  Status: {bug.get('status', 'new').upper()}")
    print(f"  Comment: {bug.get('comment', 'N/A')[:200]}")
    if bug.get('has_screenshot'):
        print(f"  📷 Screenshot: Yes ({bug.get('screenshot_size', 0)/1024:.1f} KB)")

print(f"\n💡 SUGGESTIONS: {len(suggestions)}")
for i, sug in enumerate(suggestions, 1):
    print(f"\n  Suggestion #{i}:")
    print(f"  User: {sug.get('user_email', 'N/A')}")
    print(f"  Time: {sug.get('timestamp', 'N/A')}")
    print(f"  Status: {sug.get('status', 'new').upper()}")
    print(f"  Comment: {sug.get('comment', 'N/A')[:200]}")
    if sug.get('has_screenshot'):
        print(f"  📷 Screenshot: Yes ({sug.get('screenshot_size', 0)/1024:.1f} KB)")

print(f"\n❓ QUESTIONS: {len(questions)}")
print(f"👍 PRAISE: {len(praise)}")

print("\n" + "="*80)
