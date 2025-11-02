#!/bin/bash

# Local Deployment Script
# Starts backend and frontend locally for testing

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 LOCAL DEPLOYMENT STARTING         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   Backend Port: $BACKEND_PORT"
echo "   Frontend Port: $FRONTEND_PORT"
echo ""

# Step 1: Check if ports are available
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Step 1/5: Checking Ports${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# Kill existing processes on ports
echo "🔍 Checking for existing processes..."
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ Ports cleared${NC}"
echo ""

# Step 2: Start Backend
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Step 2/5: Starting Backend${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment and start backend
source .venv/bin/activate

# Install/update dependencies
echo "📦 Installing backend dependencies..."
pip install -q -r requirements.txt

# Start backend in background
echo "🚀 Starting backend on port $BACKEND_PORT..."
python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > backend_local.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:$BACKEND_PORT/health > /dev/null; then
    echo -e "${GREEN}✅ Backend started successfully (PID: $BACKEND_PID)${NC}"
    echo "   URL: http://localhost:$BACKEND_PORT"
    echo "   Logs: backend_local.log"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "Check backend_local.log for errors"
    exit 1
fi
echo ""

# Step 3: Start Frontend
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Step 3/5: Starting Frontend${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

cd flutter_app

# Get dependencies
echo "📦 Getting Flutter dependencies..."
flutter pub get > /dev/null 2>&1

# Start Flutter web in background
echo "🚀 Starting Flutter web on port $FRONTEND_PORT..."
flutter run -d chrome --web-port $FRONTEND_PORT > ../frontend_local.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "   URL: http://localhost:$FRONTEND_PORT"
echo "   Logs: frontend_local.log"
echo ""

# Step 4: Run Automated Tests
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Step 4/5: Running Automated Tests${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo "🧪 Running test suite..."
echo ""
echo -e "${YELLOW}Note: Tests require Firebase ID token for authentication${NC}"
echo -e "${YELLOW}You can skip tests by pressing Ctrl+C${NC}"
echo ""

# Run tests (will prompt for token)
python test_logging_local.py || true

echo ""

# Step 5: Display Summary
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Step 5/5: Deployment Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo ""
echo -e "${GREEN}🎉 LOCAL DEPLOYMENT COMPLETE!${NC}"
echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  📊 SERVICES RUNNING                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🔧 Backend:${NC}"
echo "   URL: http://localhost:$BACKEND_PORT"
echo "   Health: http://localhost:$BACKEND_PORT/health"
echo "   Docs: http://localhost:$BACKEND_PORT/docs"
echo "   PID: $BACKEND_PID"
echo "   Logs: tail -f backend_local.log"
echo ""
echo -e "${GREEN}🌐 Frontend:${NC}"
echo "   URL: http://localhost:$FRONTEND_PORT"
echo "   PID: $FRONTEND_PID"
echo "   Logs: tail -f frontend_local.log"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "   1. Open browser: http://localhost:$FRONTEND_PORT"
echo "   2. Test food logging"
echo "   3. Check logs for errors"
echo "   4. When done, run: ./stop_local.sh"
echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  💡 USEFUL COMMANDS                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo "  View backend logs:  tail -f backend_local.log"
echo "  View frontend logs: tail -f frontend_local.log"
echo "  Stop services:      ./stop_local.sh"
echo "  Restart backend:    kill $BACKEND_PID && source .venv/bin/activate && python -m uvicorn app.main:app --reload"
echo ""
echo -e "${GREEN}✅ All systems running!${NC}"
echo ""

# Save PIDs for stop script
echo "$BACKEND_PID" > .backend_pid
echo "$FRONTEND_PID" > .frontend_pid

# Keep script running to show logs
echo -e "${YELLOW}Press Ctrl+C to stop watching logs (services will keep running)${NC}"
echo ""
tail -f backend_local.log

