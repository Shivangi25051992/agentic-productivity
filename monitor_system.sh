#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "╔═══════════════════════════════════════════════════════╗"
echo "║         SYSTEM MONITORING - LIVE LOGS                 ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Check if services are running
backend_status=$(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
frontend_status=$(curl -s -I http://localhost:9000 2>&1 | grep "HTTP/" | head -1)

echo -e "${CYAN}[STATUS CHECK]${NC}"
if [ "$backend_status" = "healthy" ]; then
  echo -e "  Backend:  ${GREEN}✅ RUNNING${NC} (port 8000)"
else
  echo -e "  Backend:  ${RED}❌ DOWN${NC} (port 8000)"
fi

if [ -n "$frontend_status" ]; then
  echo -e "  Frontend: ${GREEN}✅ RUNNING${NC} (port 9000)"
else
  echo -e "  Frontend: ${RED}❌ DOWN${NC} (port 9000)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}📊 MONITORING MODE ACTIVE${NC}"
echo "   Press Ctrl+C to stop monitoring"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create a timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MONITOR_LOG="/tmp/monitor_${TIMESTAMP}.log"

echo "💾 Full logs saved to: $MONITOR_LOG"
echo ""

# Function to monitor backend
monitor_backend() {
  # Try the most recent backend log file
  BACKEND_LOG=$(ls -t /tmp/backend*.log 2>/dev/null | head -1)
  if [ -z "$BACKEND_LOG" ]; then
    echo "${RED}❌ No backend log file found${NC}"
    return
  fi
  echo "📁 Monitoring backend log: $BACKEND_LOG"
  tail -f "$BACKEND_LOG" 2>/dev/null | while read line; do
    # Highlight important patterns
    if echo "$line" | grep -qi "error\|exception\|failed\|crash"; then
      echo -e "${RED}[BACKEND ERROR]${NC} $line" | tee -a "$MONITOR_LOG"
    elif echo "$line" | grep -qi "POST /chat\|GET /chat"; then
      echo -e "${GREEN}[BACKEND CHAT]${NC} $line" | tee -a "$MONITOR_LOG"
    elif echo "$line" | grep -qi "dashboard\|fitness\|timeline"; then
      echo -e "${BLUE}[BACKEND DATA]${NC} $line" | tee -a "$MONITOR_LOG"
    elif echo "$line" | grep -qi "items=\|calories\|protein"; then
      echo -e "${MAGENTA}[BACKEND NUTRITION]${NC} $line" | tee -a "$MONITOR_LOG"
    elif echo "$line" | grep -qi "200 OK\|201 Created"; then
      echo -e "${GREEN}[BACKEND SUCCESS]${NC} $line" | tee -a "$MONITOR_LOG"
    elif echo "$line" | grep -qi "4[0-9][0-9]\|5[0-9][0-9]"; then
      echo -e "${RED}[BACKEND HTTP ERROR]${NC} $line" | tee -a "$MONITOR_LOG"
    elif echo "$line" | grep -qi "INFO\|WARNING"; then
      # Don't print routine INFO logs (too noisy)
      echo "$line" >> "$MONITOR_LOG"
    else
      # Print everything else with timestamp
      echo "[BACKEND] $line" | tee -a "$MONITOR_LOG"
    fi
  done
}

# Function to monitor frontend
monitor_flutter() {
  tail -f /tmp/flutter_final.log 2>/dev/null | while read line; do
    if echo "$line" | grep -qi "error\|exception\|failed"; then
      echo -e "${RED}[FRONTEND ERROR]${NC} $line" | tee -a "$MONITOR_LOG"
    elif echo "$line" | grep -qi "hot reload\|hot restart"; then
      echo -e "${YELLOW}[FRONTEND RELOAD]${NC} $line" | tee -a "$MONITOR_LOG"
    elif echo "$line" | grep -qi "compilation"; then
      echo -e "${CYAN}[FRONTEND BUILD]${NC} $line" | tee -a "$MONITOR_LOG"
    else
      echo "[FRONTEND] $line" >> "$MONITOR_LOG"
    fi
  done
}

# Run both monitors in parallel
monitor_backend &
BACKEND_PID=$!

monitor_flutter &
FLUTTER_PID=$!

# Trap Ctrl+C to cleanup
trap "echo ''; echo 'Stopping monitoring...'; kill $BACKEND_PID $FLUTTER_PID 2>/dev/null; exit 0" INT

# Keep script running
wait

