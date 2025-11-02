#!/bin/bash

# Get admin token
echo "🔐 Getting admin token..."
TOKEN=$(curl -s -X POST "https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get admin token"
  exit 1
fi

echo "✅ Got admin token"
echo ""

# Search for user
echo "🔍 Searching for user: tets@teste.com"
echo "=================================="

# Get user list and search
curl -s -X GET "https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/admin/users" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
users = data.get('users', [])
found = False
for user in users:
    if 'teste' in user.get('email', '').lower() or 'test@test' in user.get('email', '').lower():
        found = True
        print(f\"✅ Found user:\")
        print(f\"  Email: {user.get('email')}\")
        print(f\"  User ID: {user.get('user_id')}\")
        print(f\"  Name: {user.get('display_name', 'N/A')}\")
        print(f\"  Created: {user.get('created_at', 'N/A')}\")
        print(f\"  Last Login: {user.get('last_login', 'N/A')}\")
        
        # Save user_id for next query
        with open('/tmp/user_id.txt', 'w') as f:
            f.write(user.get('user_id', ''))
        break

if not found:
    print('❌ User not found')
    print('Available users:')
    for user in users[:5]:
        print(f\"  - {user.get('email')}\")
"

if [ ! -f /tmp/user_id.txt ]; then
  echo "❌ Could not find user"
  exit 1
fi

USER_ID=$(cat /tmp/user_id.txt)
echo ""
echo "📊 Fetching detailed data for user: $USER_ID"
echo "=================================="

# Get fitness logs
echo ""
echo "🍽️  RECENT FITNESS LOGS:"
echo "---"
curl -s -X GET "https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/fitness/logs?limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-ID: $USER_ID" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    logs = data.get('logs', [])
    if not logs:
        print('❌ No fitness logs found')
    else:
        for i, log in enumerate(logs[:5], 1):
            print(f\"\nLog {i}:\")
            print(f\"  Category: {log.get('category', 'N/A')}\")
            print(f\"  Item: {log.get('item', 'N/A')}\")
            print(f\"  Meal Type: {log.get('meal_type', 'N/A')}\")
            print(f\"  Calories: {log.get('calories', 0)}\")
            print(f\"  Time: {log.get('timestamp', 'N/A')}\")
            print(f\"  Summary: {log.get('summary', 'N/A')[:80]}\")
except Exception as e:
    print(f'Error: {e}')
"

# Get profile
echo ""
echo "👤 USER PROFILE:"
echo "---"
curl -s -X GET "https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/profile/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-ID: $USER_ID" | python3 -c "
import sys, json
try:
    profile = json.load(sys.stdin)
    print(f\"Name: {profile.get('name', 'N/A')}\")
    print(f\"Timezone: {profile.get('timezone', '❌ NOT SET')}\")
    print(f\"Units: {profile.get('units', 'N/A')}\")
    print(f\"Age: {profile.get('age', 'N/A')}\")
    print(f\"Weight: {profile.get('weight', 'N/A')} kg\")
    print(f\"Height: {profile.get('height', 'N/A')} cm\")
    print(f\"Goal: {profile.get('fitness_goal', 'N/A')}\")
    print(f\"Activity Level: {profile.get('activity_level', 'N/A')}\")
    print(f\"Daily Calories: {profile.get('daily_calories', 'N/A')}\")
except Exception as e:
    print(f'Error: {e}')
"

rm -f /tmp/user_id.txt
