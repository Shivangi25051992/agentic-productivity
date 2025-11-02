#!/bin/bash
# Automated Test Runner
# Runs all automated tests and reports results

echo "================================================================================"
echo "🤖 AUTOMATED TEST SUITE"
echo "================================================================================"
echo ""

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
    BACKEND_URL="http://localhost:8000"
elif curl -s https://aiproductivity-backend-productivityai-mvp.us-central1.run.app/health > /dev/null 2>&1; then
    echo "✅ Using cloud backend"
    BACKEND_URL="https://aiproductivity-backend-productivityai-mvp.us-central1.run.app"
else
    echo "❌ Backend is not running"
    echo "   Start local: cd app && uvicorn main:app --reload"
    echo "   Or set BACKEND_URL to cloud URL"
    exit 1
fi

echo ""
echo "🔧 Backend URL: $BACKEND_URL"
echo ""

# Set environment variables
export BACKEND_URL=$BACKEND_URL
export FIREBASE_API_KEY="AIzaSyBLb8tqVHY5KZ9X0YmQKxJ0aVYPUZxQKxY"

# Run tests
echo "================================================================================"
echo "🚀 RUNNING AUTOMATED TESTS"
echo "================================================================================"
echo ""

cd "$(dirname "$0")"
python3 test_all_features.py

# Capture exit code
EXIT_CODE=$?

echo ""
echo "================================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ ALL TESTS PASSED - SAFE TO DEPLOY"
else
    echo "❌ TESTS FAILED - DO NOT DEPLOY"
fi
echo "================================================================================"

exit $EXIT_CODE

