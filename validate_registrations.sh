#!/bin/bash

################################################################################
# Registration Validation Script
# 
# Validates that all providers and routers are properly registered
# Prevents deployment of features with missing registrations
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

PROJECT_ROOT="/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity"
cd "$PROJECT_ROOT"

VALIDATION_FAILED=false

################################################################################
# 1. Validate Flutter Providers
################################################################################

log_info "Validating Flutter providers..."

# Find all provider files
PROVIDER_FILES=$(find flutter_app/lib/providers -name "*_provider.dart" 2>/dev/null | grep -v ".g.dart" || true)

if [ -n "$PROVIDER_FILES" ]; then
    while IFS= read -r provider_file; do
        provider_name=$(basename "$provider_file" .dart)
        provider_class=$(echo "$provider_name" | sed 's/_\([a-z]\)/\U\1/g' | sed 's/^./\U&/')
        
        # Check if imported in main.dart
        if ! grep -q "import.*providers/${provider_name}.dart" flutter_app/lib/main.dart; then
            log_error "Provider ${provider_class} not imported in main.dart"
            VALIDATION_FAILED=true
        fi
        
        # Check if registered (look for the class name in MultiProvider)
        if ! grep -q "${provider_class}" flutter_app/lib/main.dart; then
            log_error "Provider ${provider_class} not registered in MultiProvider"
            VALIDATION_FAILED=true
        fi
    done <<< "$PROVIDER_FILES"
    
    if [ "$VALIDATION_FAILED" = false ]; then
        log_success "All Flutter providers are properly registered"
    fi
else
    log_warning "No provider files found"
fi

################################################################################
# 2. Validate Backend Routers
################################################################################

log_info "Validating backend routers..."

# Find all router files
ROUTER_FILES=$(find app/routers -name "*.py" 2>/dev/null | grep -v "__pycache__" | grep -v "__init__.py" || true)

if [ -n "$ROUTER_FILES" ]; then
    while IFS= read -r router_file; do
        router_name=$(basename "$router_file" .py)
        
        # Check if imported in main.py
        if ! grep -q "from app.routers.${router_name} import router" app/main.py && \
           ! grep -q "from app.routers import.*${router_name}" app/main.py; then
            log_warning "Router ${router_name} may not be imported in main.py"
        fi
        
        # Check if registered (look for include_router)
        if ! grep -q "include_router.*${router_name}" app/main.py && \
           ! grep -q "app.include_router" app/main.py | grep -q "${router_name}"; then
            log_warning "Router ${router_name} may not be registered in main.py"
        fi
    done <<< "$ROUTER_FILES"
    
    log_success "Backend router validation complete"
else
    log_warning "No router files found"
fi

################################################################################
# 3. Check for Common Registration Patterns
################################################################################

log_info "Checking for common registration patterns..."

# Check Flutter main.dart has MultiProvider
if ! grep -q "MultiProvider" flutter_app/lib/main.dart; then
    log_error "MultiProvider not found in flutter_app/lib/main.dart"
    VALIDATION_FAILED=true
fi

# Check backend main.py has FastAPI app
if ! grep -q "app = FastAPI" app/main.py; then
    log_error "FastAPI app not found in app/main.py"
    VALIDATION_FAILED=true
fi

################################################################################
# 4. Semantic Dependency Detection
################################################################################

log_info "Checking for semantic dependencies..."

# Get changed files between local and production
CHANGED_FILES=$(git diff production..local --name-only 2>/dev/null || echo "")

if [ -n "$CHANGED_FILES" ]; then
    # Check if new providers were added
    NEW_PROVIDERS=$(echo "$CHANGED_FILES" | grep "flutter_app/lib/providers/.*_provider.dart" || true)
    if [ -n "$NEW_PROVIDERS" ]; then
        if ! echo "$CHANGED_FILES" | grep -q "flutter_app/lib/main.dart"; then
            log_warning "New providers added but main.dart not changed"
            log_warning "Did you register the providers?"
        fi
    fi
    
    # Check if new routers were added
    NEW_ROUTERS=$(echo "$CHANGED_FILES" | grep "app/routers/.*\.py" || true)
    if [ -n "$NEW_ROUTERS" ]; then
        if ! echo "$CHANGED_FILES" | grep -q "app/main.py"; then
            log_warning "New routers added but main.py not changed"
            log_warning "Did you register the routers?"
        fi
    fi
fi

################################################################################
# Summary
################################################################################

echo ""
if [ "$VALIDATION_FAILED" = true ]; then
    log_error "Registration validation FAILED"
    log_error "Please fix the issues above before deploying"
    exit 1
else
    log_success "All registration validations passed"
    exit 0
fi

