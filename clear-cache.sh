#!/bin/bash

echo "🧹 Clearing all caches and preparing for manual testing..."
echo ""

# Stop servers
echo "1️⃣ Stopping all servers..."
./stop-dev.sh 2>/dev/null || echo "   No servers running"
sleep 2

# Clear Python cache
echo ""
echo "2️⃣ Clearing Python cache..."
rm -rf .pytest_cache
rm -rf __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "   ✅ Python cache cleared"

# Clear Flutter cache
echo ""
echo "3️⃣ Clearing Flutter cache..."
cd flutter_app
flutter clean
flutter pub get
cd ..
echo "   ✅ Flutter cache cleared"

# Clear test data (optional)
echo ""
echo "4️⃣ Clearing test data..."
rm -f tests/test_users.json
rm -f tests/*.log
rm -f tests/simulation_report.json
echo "   ✅ Test data cleared"

# Clear backend logs
echo ""
echo "5️⃣ Clearing backend logs..."
rm -f *.log
rm -f backend*.log
echo "   ✅ Backend logs cleared"

echo ""
echo "✅ All caches cleared!"
echo ""
echo "📋 Next steps:"
echo "   1. Start servers: ./start-dev.sh"
echo "   2. Open browser: http://localhost:8080"
echo "   3. Follow: MANUAL_TESTING_GUIDE.md"
echo ""

