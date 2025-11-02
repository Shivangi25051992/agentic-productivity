#!/bin/bash

# Get admin token
TOKEN=$(curl -s -X POST "https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo "✅ Got admin token"
echo ""

# Get all users and find test user
echo "🔍 Searching for user: tets@teste.com or test@test.com"
echo "================================================================"

curl -s -X GET "https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/admin/users" \
  -H "Authorization: Bearer $TOKEN" > /tmp/users.json

python3 << 'PYTHON'
import json

with open('/tmp/users.json') as f:
    data = json.load(f)

users = data.get('users', [])
print(f"Total users found: {len(users)}\n")

# Find test user
test_user = None
for user in users:
    email = user.get('email', '').lower()
    if 'teste' in email or 'test@test' in email:
        test_user = user
        print(f"✅ FOUND USER:")
        print(f"  Email: {user.get('email')}")
        print(f"  User ID: {user.get('user_id')}")
        print(f"  Display Name: {user.get('display_name', 'N/A')}")
        print(f"  Created: {user.get('created_at', 'N/A')}")
        
        # Save for next query
        with open('/tmp/user_id.txt', 'w') as f:
            f.write(user.get('user_id', ''))
        break

if not test_user:
    print("❌ User not found. Available users:")
    for u in users[:10]:
        print(f"  - {u.get('email')}")
PYTHON

if [ ! -f /tmp/user_id.txt ]; then
    echo "❌ Could not find user"
    exit 1
fi

USER_ID=$(cat /tmp/user_id.txt)
echo ""
echo "================================================================"
echo "📊 DETAILED USER DATA"
echo "================================================================"

# Get profile via admin endpoint
echo ""
echo "👤 USER PROFILE (via /profile/me with X-User-ID):"
echo "---"
curl -s -X GET "https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/profile/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-ID: $USER_ID" | python3 -m json.tool

# Get fitness logs
echo ""
echo "🍽️  RECENT FITNESS LOGS (Last 10):"
echo "---"
curl -s -X GET "https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/fitness/logs?limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-ID: $USER_ID" | python3 << 'PYTHON'
import sys, json
data = json.load(sys.stdin)
logs = data.get('logs', [])

if not logs:
    print("❌ No fitness logs found")
else:
    print(f"Total logs: {len(logs)}\n")
    for i, log in enumerate(logs, 1):
        print(f"Log #{i}:")
        print(f"  Category: {log.get('category', 'N/A')}")
        print(f"  Item: {log.get('item', 'N/A')}")
        print(f"  Meal Type: {log.get('meal_type', 'N/A')}")
        print(f"  Calories: {log.get('calories', 0)}")
        print(f"  Timestamp: {log.get('timestamp', 'N/A')}")
        print(f"  Summary: {log.get('summary', 'N/A')}")
        print()
PYTHON

# Clean up
rm -f /tmp/users.json /tmp/user_id.txt

