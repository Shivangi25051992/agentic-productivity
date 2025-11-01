#!/bin/bash

# AI Productivity App - Development Server Startup Script
# This script starts both the FastAPI backend and Flutter frontend

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT"
FRONTEND_DIR="$PROJECT_ROOT/flutter_app"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   AI Productivity App - Development Environment       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if .env.local exists
if [ ! -f "$BACKEND_DIR/.env.local" ]; then
    echo -e "${RED}✗ Error: .env.local not found!${NC}"
    echo -e "${YELLOW}Please create .env.local with required environment variables.${NC}"
    echo -e "${YELLOW}See .env.example for reference.${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo -e "${RED}✗ Error: Python virtual environment not found!${NC}"
    echo -e "${YELLOW}Run: python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

# Start Backend Server
echo -e "${GREEN}[1/2] Starting FastAPI Backend...${NC}"
cd "$BACKEND_DIR"
source .venv/bin/activate

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠ Port 8000 is already in use. Killing existing process...${NC}"
    kill -9 $(lsof -t -i:8000) 2>/dev/null || true
    sleep 2
fi

# Start uvicorn in background
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "${BLUE}  → API: http://localhost:8000${NC}"
echo -e "${BLUE}  → Admin Panel: http://localhost:8000/admin${NC}"
echo -e "${BLUE}  → Logs: $PROJECT_ROOT/backend.log${NC}"
echo ""

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Backend failed to start. Check backend.log for errors.${NC}"
        tail -n 20 "$PROJECT_ROOT/backend.log"
        cleanup
    fi
    sleep 1
done
echo ""

# Start Flutter Frontend
echo -e "${GREEN}[2/2] Starting Flutter Frontend...${NC}"
cd "$FRONTEND_DIR"

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}✗ Error: Flutter is not installed or not in PATH!${NC}"
    echo -e "${YELLOW}Install Flutter: https://docs.flutter.dev/get-started/install${NC}"
    cleanup
fi

# Get Flutter dependencies
echo -e "${YELLOW}⏳ Getting Flutter dependencies...${NC}"
flutter pub get > /dev/null 2>&1

# Check if Chrome is available for web
FLUTTER_DEVICE="chrome"
if ! flutter devices | grep -q "Chrome"; then
    echo -e "${YELLOW}⚠ Chrome not available, checking for other devices...${NC}"
    FLUTTER_DEVICE=$(flutter devices | grep -v "No devices" | grep -v "Chrome" | head -n 1 | awk '{print $1}')
    if [ -z "$FLUTTER_DEVICE" ]; then
        echo -e "${RED}✗ No Flutter devices available!${NC}"
        cleanup
    fi
fi

# Start Flutter in background with FIXED PORT
echo -e "${YELLOW}⏳ Starting Flutter app (this may take a minute)...${NC}"
flutter run -d "$FLUTTER_DEVICE" --web-port=8080 --web-hostname=localhost --dart-define=API_BASE_URL=http://localhost:8000 > "$PROJECT_ROOT/frontend.log" 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✓ Flutter started (PID: $FRONTEND_PID)${NC}"
echo -e "${BLUE}  → App URL: http://localhost:8080${NC}"
echo -e "${BLUE}  → Logs: $PROJECT_ROOT/frontend.log${NC}"
echo ""

# Wait a bit for Flutter to start
sleep 5

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   🚀 Development Environment Ready!                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Backend:${NC}"
echo -e "  • API: http://localhost:8000"
echo -e "  • Admin Panel: http://localhost:8000/admin"
echo -e "  • Docs: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Frontend:${NC}"
echo -e "  • Check browser for Flutter app"
echo -e "  • Or check frontend.log for URL"
echo ""
echo -e "${BLUE}Test Credentials:${NC}"
echo -e "  • Email: tester@example.com"
echo -e "  • Password: Test1234!"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo -e "  • Backend: tail -f backend.log"
echo -e "  • Frontend: tail -f frontend.log"
echo ""
echo -e "${RED}Press Ctrl+C to stop all servers${NC}"
echo ""

# Keep script running and show live backend logs
tail -f "$PROJECT_ROOT/backend.log" &
wait

