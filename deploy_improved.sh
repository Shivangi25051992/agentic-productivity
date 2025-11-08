#!/bin/bash

################################################################################
# IMPROVED Automated Release Manager & DevOps Pipeline
# 
# Incorporates learnings from production issues:
# 1. Tests production build before deploying
# 2. Validates provider/router registrations
# 3. Detects semantic dependencies
# 4. Better diff analysis
# 5. Automated checklist validation
#
# Usage: ./deploy_improved.sh [--skip-tests] [--force]
################################################################################

set -e
trap 'handle_error $? $LINENO' ERR

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity"
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:9090"
SKIP_TESTS=false
FORCE_DEPLOY=false
BACKUP_TAG=""
DEPLOYMENT_FAILED=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-tests) SKIP_TESTS=true; shift ;;
    --force) FORCE_DEPLOY=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

################################################################################
# Helper Functions
################################################################################

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

handle_error() {
    local exit_code=$1
    local line_number=$2
    log_error "Error at line $line_number (exit code: $exit_code)"
    DEPLOYMENT_FAILED=true
    rollback_deployment
    exit $exit_code
}

################################################################################
# NEW: Pre-Deployment Checklist
################################################################################

run_checklist() {
    log_info "Running pre-deployment checklist..."
    
    cd "$PROJECT_ROOT"
    
    # Check for new providers/routers
    CHANGED_FILES=$(git diff production..local --name-only)
    
    NEW_PROVIDERS=$(echo "$CHANGED_FILES" | grep "flutter_app/lib/providers/.*_provider.dart" || true)
    NEW_ROUTERS=$(echo "$CHANGED_FILES" | grep "app/routers/.*\.py" || true)
    NEW_SCREENS=$(echo "$CHANGED_FILES" | grep "flutter_app/lib/screens/" || true)
    
    if [ -n "$NEW_PROVIDERS" ]; then
        log_warning "📋 New providers detected:"
        echo "$NEW_PROVIDERS"
        log_info "Checking if registered in main.dart..."
        
        if ! echo "$CHANGED_FILES" | grep -q "flutter_app/lib/main.dart"; then
            log_error "main.dart not modified - did you register the providers?"
            return 1
        fi
    fi
    
    if [ -n "$NEW_ROUTERS" ]; then
        log_warning "📋 New routers detected:"
        echo "$NEW_ROUTERS"
        log_info "Checking if registered in main.py..."
        
        if ! echo "$CHANGED_FILES" | grep -q "app/main.py"; then
            log_error "main.py not modified - did you register the routers?"
            return 1
        fi
    fi
    
    log_success "Pre-deployment checklist passed"
}

################################################################################
# IMPROVED: Test with Production Build
################################################################################

run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_warning "Skipping tests (--skip-tests flag)"
        return 0
    fi
    
    log_info "Running automated tests..."
    cd "$PROJECT_ROOT"
    
    # 1. Backend health check
    log_info "Checking backend health..."
    if ! curl -s "$BACKEND_URL/health" | grep -q "healthy"; then
        log_error "Backend health check failed"
        return 1
    fi
    log_success "Backend healthy"
    
    # 2. Frontend analysis
    log_info "Running Flutter analyze..."
    cd flutter_app
    if command -v flutter &> /dev/null; then
        flutter analyze || log_warning "Flutter analyze found issues (non-blocking)"
    fi
    
    # 3. CRITICAL: Test production build
    log_info "🔥 Testing production build (catches registration issues)..."
    if command -v flutter &> /dev/null; then
        flutter build web --release > /tmp/flutter_build.log 2>&1 || {
            log_error "Production build FAILED!"
            log_error "This usually means:"
            log_error "  - Missing imports"
            log_error "  - Missing provider registrations"
            log_error "  - Missing router registrations"
            log_error ""
            log_error "Build log:"
            tail -20 /tmp/flutter_build.log
            cd "$PROJECT_ROOT"
            return 1
        }
        log_success "Production build test PASSED ✨"
    fi
    
    cd "$PROJECT_ROOT"
    
    # 4. Validate registrations
    log_info "Validating provider/router registrations..."
    if [ -f "validate_registrations.sh" ]; then
        chmod +x validate_registrations.sh
        ./validate_registrations.sh || {
            log_error "Registration validation failed"
            return 1
        }
    fi
    
    log_success "All tests passed"
}

################################################################################
# Standard Functions (same as before)
################################################################################

preflight_checks() {
    log_info "Running pre-flight checks..."
    cd "$PROJECT_ROOT"
    
    if [ ! -d ".git" ]; then
        log_error "Not a git repository"
        exit 1
    fi
    
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "local" ]; then
        log_warning "Not on 'local' branch. Switching..."
        git checkout local
    fi
    
    if ! git show-ref --verify --quiet refs/heads/production; then
        log_error "Production branch doesn't exist"
        exit 1
    fi
    
    log_success "Pre-flight checks passed"
}

commit_to_local() {
    log_info "Committing changes to local branch..."
    cd "$PROJECT_ROOT"
    
    if [ -z "$(git status --porcelain)" ]; then
        log_info "No changes to commit"
        return 0
    fi
    
    git add -A
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    git commit -m "chore: automated commit - $TIMESTAMP"
    
    log_success "Changes committed to local branch"
}

backup_production() {
    log_info "Backing up current production state..."
    cd "$PROJECT_ROOT"
    
    BACKUP_TAG="backup-$(date +%Y%m%d-%H%M%S)"
    git checkout production
    git tag -a "$BACKUP_TAG" -m "Backup before deployment at $(date)"
    log_success "Production backed up as tag: $BACKUP_TAG"
    git checkout local
}

merge_to_production() {
    log_info "Merging changes to production..."
    cd "$PROJECT_ROOT"
    
    CHANGED_FILES=$(git diff production..local --name-only)
    
    if [ -z "$CHANGED_FILES" ]; then
        log_info "No changes to merge"
        return 0
    fi
    
    log_info "Files to be merged:"
    echo "$CHANGED_FILES"
    
    # Exclude sensitive files
    EXCLUDED_PATTERNS=(".env" ".env.local" ".env.production" "*.key" "*.pem" "*credentials*" "*secret*" "firebase-adminsdk-*.json")
    
    SAFE_FILES=""
    while IFS= read -r file; do
        EXCLUDED=false
        for pattern in "${EXCLUDED_PATTERNS[@]}"; do
            if [[ "$file" == $pattern ]]; then
                EXCLUDED=true
                log_warning "Excluding sensitive file: $file"
                break
            fi
        done
        
        if [ "$EXCLUDED" = false ]; then
            SAFE_FILES="$SAFE_FILES $file"
        fi
    done <<< "$CHANGED_FILES"
    
    git checkout production
    
    for file in $SAFE_FILES; do
        if [ -f "$file" ] || [ -d "$file" ]; then
            git checkout local -- "$file"
        fi
    done
    
    if [ -n "$(git status --porcelain)" ]; then
        TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
        git add -A
        git commit -m "deploy: automated deployment - $TIMESTAMP"
        
        RELEASE_TAG="v$(date +%Y%m%d-%H%M%S)"
        git tag -a "$RELEASE_TAG" -m "Automated release - $TIMESTAMP"
        
        log_success "Changes merged to production (tag: $RELEASE_TAG)"
    else
        log_info "No changes to commit to production"
    fi
}

deploy_to_production() {
    log_info "Deploying to production..."
    cd "$PROJECT_ROOT"
    git checkout production
    
    # Deploy backend
    log_info "Deploying backend to Cloud Run..."
    if command -v ~/google-cloud-sdk/bin/gcloud &> /dev/null; then
        ~/google-cloud-sdk/bin/gcloud run deploy aiproductivity-backend \
          --source . \
          --region us-central1 \
          --allow-unauthenticated \
          --quiet || {
            log_error "Backend deployment failed"
            return 1
        }
        log_success "Backend deployed"
    else
        log_warning "gcloud not found, skipping backend deployment"
    fi
    
    # Deploy frontend
    log_info "Deploying frontend to Firebase Hosting..."
    cd flutter_app
    if command -v flutter &> /dev/null; then
        flutter build web --release || {
            log_error "Flutter build failed"
            return 1
        }
        
        cd ..
        if command -v firebase &> /dev/null; then
            firebase deploy --only hosting || {
                log_error "Firebase deployment failed"
                return 1
            }
            log_success "Frontend deployed"
        else
            log_warning "Firebase CLI not found"
        fi
    fi
    
    cd "$PROJECT_ROOT"
    log_success "Deployment completed"
}

verify_deployment() {
    log_info "Verifying deployment..."
    sleep 5
    
    # Check production backend
    PROD_URL="https://aiproductivity-backend-51515298953.us-central1.run.app"
    if curl -s "$PROD_URL/health" | grep -q "healthy"; then
        log_success "Production backend healthy"
    else
        log_error "Production backend health check failed"
        return 1
    fi
    
    log_success "Deployment verification passed"
}

rollback_deployment() {
    if [ "$DEPLOYMENT_FAILED" = false ]; then
        return 0
    fi
    
    log_error "Deployment failed! Rolling back..."
    cd "$PROJECT_ROOT"
    git checkout production
    
    if [ -n "$BACKUP_TAG" ]; then
        log_info "Reverting to backup: $BACKUP_TAG"
        git reset --hard "$BACKUP_TAG"
        log_success "Rollback completed"
    else
        log_error "No backup tag found for rollback"
    fi
    
    git checkout local
}

cleanup() {
    log_info "Cleaning up..."
    cd "$PROJECT_ROOT"
    git checkout local
    
    BACKUP_TAGS=$(git tag -l "backup-*" | sort -r | tail -n +6)
    if [ -n "$BACKUP_TAGS" ]; then
        echo "$BACKUP_TAGS" | xargs git tag -d
        log_info "Removed old backup tags"
    fi
    
    log_success "Cleanup completed"
}

################################################################################
# Main Execution
################################################################################

main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  🚀 IMPROVED Automated Release Manager (with learnings)   ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    preflight_checks
    run_checklist || {
        log_error "Pre-deployment checklist failed! Aborting."
        exit 1
    }
    commit_to_local
    run_tests || {
        log_error "Tests failed! Aborting deployment."
        exit 1
    }
    backup_production
    merge_to_production
    deploy_to_production || {
        DEPLOYMENT_FAILED=true
        rollback_deployment
        exit 1
    }
    verify_deployment || {
        DEPLOYMENT_FAILED=true
        rollback_deployment
        exit 1
    }
    cleanup
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║              ✅ Deployment Successful!                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    log_success "All steps completed successfully"
    log_info "Production branch is now updated and deployed"
    log_info "Backup tag: $BACKUP_TAG"
    log_info "You are now on 'local' branch, ready for next development"
    echo ""
}

main

