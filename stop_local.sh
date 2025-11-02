#!/bin/bash

# Stop Local Deployment Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🛑 STOPPING LOCAL SERVICES           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Read PIDs from files
if [ -f ".backend_pid" ]; then
    BACKEND_PID=$(cat .backend_pid)
    echo "🔴 Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || true
    rm .backend_pid
    echo -e "${GREEN}✅ Backend stopped${NC}"
else
    echo -e "${YELLOW}⚠️  No backend PID file found${NC}"
fi

if [ -f ".frontend_pid" ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    echo "🔴 Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || true
    rm .frontend_pid
    echo -e "${GREEN}✅ Frontend stopped${NC}"
else
    echo -e "${YELLOW}⚠️  No frontend PID file found${NC}"
fi

# Kill any remaining processes on ports
echo ""
echo "🧹 Cleaning up ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ All local services stopped!${NC}"
echo ""

