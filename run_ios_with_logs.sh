#!/bin/bash
# Run iOS app with proper API URL and show logs

cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/flutter_app

echo "🚀 Starting iOS app build..."
echo "📱 Device: iPhone 16e"
echo "🌐 API URL: http://192.168.0.115:8000"
echo ""

flutter run \
  -d D4F4433D-10A6-4B44-904C-150818724C45 \
  --dart-define=API_BASE_URL=http://192.168.0.115:8000 \
  -v


