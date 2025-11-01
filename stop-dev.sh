#!/bin/bash

# AI Productivity App - Stop Development Servers Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping AI Productivity App servers...${NC}"

# Stop backend (port 8000)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⏳ Stopping backend server (port 8000)...${NC}"
    kill -9 $(lsof -t -i:8000) 2>/dev/null
    echo -e "${GREEN}✓ Backend stopped${NC}"
else
    echo -e "${YELLOW}ℹ Backend not running${NC}"
fi

# Stop Flutter processes
if pgrep -f "flutter run" > /dev/null; then
    echo -e "${YELLOW}⏳ Stopping Flutter app...${NC}"
    pkill -f "flutter run"
    echo -e "${GREEN}✓ Flutter stopped${NC}"
else
    echo -e "${YELLOW}ℹ Flutter not running${NC}"
fi

# Clean up log files
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$PROJECT_ROOT/backend.log" ]; then
    rm "$PROJECT_ROOT/backend.log"
fi
if [ -f "$PROJECT_ROOT/frontend.log" ]; then
    rm "$PROJECT_ROOT/frontend.log"
fi

echo -e "${GREEN}✓ All servers stopped${NC}"





