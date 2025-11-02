#!/bin/bash

PROJECT_ID="productivityai-mvp"
FIREBASE_API_KEY="AIzaSyBfQQoB7YvN3vLe5xMJvqRmK8pWXyZzE4M"

echo "🔍 Querying Firestore for user: tets@teste.com"
echo "================================================================"

# Query users collection
curl -s "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/users" | python3 << 'PYTHON'
import json, sys

try:
    data = json.load(sys.stdin)
    documents = data.get('documents', [])
    
    print(f"Total users in 'users' collection: {len(documents)}\n")
    
    for doc in documents:
        fields = doc.get('fields', {})
        email = fields.get('email', {}).get('stringValue', 'N/A')
        user_id = doc.get('name', '').split('/')[-1]
        
        if 'teste' in email.lower() or 'test@test' in email.lower():
            print(f"✅ FOUND USER:")
            print(f"  User ID: {user_id}")
            print(f"  Email: {email}")
            print(f"  Created: {fields.get('created_at', {}).get('timestampValue', 'N/A')}")
            
            # Save user_id
            with open('/tmp/found_user_id.txt', 'w') as f:
                f.write(user_id)
            break
    else:
        print("❌ User not found in 'users' collection")
        print("\nShowing first 5 users:")
        for doc in documents[:5]:
            fields = doc.get('fields', {})
            email = fields.get('email', {}).get('stringValue', 'N/A')
            print(f"  - {email}")
            
except Exception as e:
    print(f"Error: {e}")
    print(sys.stdin.read())
PYTHON

if [ -f /tmp/found_user_id.txt ]; then
    USER_ID=$(cat /tmp/found_user_id.txt)
    echo ""
    echo "================================================================"
    echo "📊 USER PROFILE DATA"
    echo "================================================================"
    
    # Get user profile
    curl -s "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/user_profiles/$USER_ID" | python3 << 'PYTHON'
import json, sys

try:
    data = json.load(sys.stdin)
    fields = data.get('fields', {})
    
    print("\n👤 USER PROFILE:")
    print(f"  Name: {fields.get('name', {}).get('stringValue', 'N/A')}")
    print(f"  Timezone: {fields.get('timezone', {}).get('stringValue', '❌ NOT SET')}")
    print(f"  Units: {fields.get('units', {}).get('stringValue', 'N/A')}")
    print(f"  Age: {fields.get('age', {}).get('integerValue', 'N/A')}")
    print(f"  Weight: {fields.get('weight', {}).get('doubleValue', 'N/A')} kg")
    print(f"  Height: {fields.get('height', {}).get('doubleValue', 'N/A')} cm")
    print(f"  Goal: {fields.get('fitness_goal', {}).get('stringValue', 'N/A')}")
    print(f"  Activity: {fields.get('activity_level', {}).get('stringValue', 'N/A')}")
    print(f"  Daily Calories: {fields.get('daily_calories', {}).get('integerValue', 'N/A')}")
    
except Exception as e:
    print(f"Error: {e}")
PYTHON

    echo ""
    echo "================================================================"
    echo "🍽️  FITNESS LOGS"
    echo "================================================================"
    
    # Get fitness logs from subcollection
    curl -s "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/users/$USER_ID/fitness_logs?pageSize=10&orderBy=timestamp%20desc" | python3 << 'PYTHON'
import json, sys

try:
    data = json.load(sys.stdin)
    documents = data.get('documents', [])
    
    if not documents:
        print("\n❌ No fitness logs found in subcollection")
    else:
        print(f"\nTotal logs: {len(documents)}\n")
        for i, doc in enumerate(documents, 1):
            fields = doc.get('fields', {})
            print(f"Log #{i}:")
            print(f"  Category: {fields.get('category', {}).get('stringValue', 'N/A')}")
            print(f"  Item: {fields.get('item', {}).get('stringValue', 'N/A')}")
            print(f"  Meal Type: {fields.get('meal_type', {}).get('stringValue', 'N/A')}")
            print(f"  Calories: {fields.get('calories', {}).get('integerValue', 'N/A')}")
            print(f"  Timestamp: {fields.get('timestamp', {}).get('timestampValue', 'N/A')}")
            print(f"  Summary: {fields.get('summary', {}).get('stringValue', 'N/A')}")
            print()
            
except Exception as e:
    print(f"Error: {e}")
PYTHON

    rm -f /tmp/found_user_id.txt
fi

