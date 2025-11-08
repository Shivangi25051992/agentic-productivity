#!/bin/bash
# Test if backend is returning Phase 2 fields

echo "🧪 Testing Phase 2 Backend Response..."
echo ""

# Get auth token (you'll need to replace this with a real token)
echo "NOTE: This test requires authentication. Checking unauthenticated endpoint instead..."
echo ""

# Test the debug endpoint (no auth required)
echo "Testing /test/chat-debug endpoint:"
curl -s -X POST "http://localhost:8000/test/chat-debug?text=2+eggs" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('status') == 'success':
        resp = data.get('response', {})
        print('✅ Backend Test: SUCCESS')
        print(f\"   - confidence_score: {resp.get('confidence_score')}\")
        print(f\"   - confidence_level: {resp.get('confidence_level')}\")
        print(f\"   - explanation: {'Present' if resp.get('explanation') else 'None'}\")
        print(f\"   - alternatives: {resp.get('alternatives', 'None')}\")
        print(f\"   - summary: {resp.get('summary', 'None')[:50]}...\")
        print(f\"   - suggestion: {resp.get('suggestion', 'None')[:50]}...\")
    else:
        print('❌ Backend Test: FAILED')
        print(f\"   Error: {data.get('error_message')}\")
except Exception as e:
    print(f'❌ Parse Error: {e}')
"

echo ""
echo "✅ If you see confidence_score and explanation above, backend is working!"
echo "❌ If they're None, backend Phase 2 is not working."




