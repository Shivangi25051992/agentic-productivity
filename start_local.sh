#!/bin/bash

echo "🚀 Starting Local Development Environment"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "❌ ERROR: .env.local not found!"
    echo "Please create .env.local with required environment variables"
    exit 1
fi

echo "✅ Environment ready!"
echo ""
echo "=========================================="
echo "🎯 NEXT STEPS:"
echo "=========================================="
echo ""
echo "1. Start Backend (Terminal 1):"
echo "   cd app && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. Start Frontend (Terminal 2):"
echo "   cd flutter_app && flutter run -d chrome"
echo ""
echo "3. Update Frontend API URL:"
echo "   Edit: flutter_app/lib/utils/constants.dart"
echo "   Change apiBaseUrl to: 'http://localhost:8000'"
echo ""
echo "=========================================="
echo "📊 USEFUL COMMANDS:"
echo "=========================================="
echo ""
echo "Test backend health:"
echo "  curl http://localhost:8000/health"
echo ""
echo "Check backend logs:"
echo "  tail -f app/logs/*.log"
echo ""
echo "Flutter logs:"
echo "  flutter logs"
echo ""
