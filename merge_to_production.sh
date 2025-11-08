#!/bin/bash

# Merge Local Changes to Production
# Usage: ./merge_to_production.sh

set -e  # Exit on error

echo "🌿 Git Branching: Merge Local → Production"
echo "=========================================="
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"
echo ""

# Show what will be merged
echo "📊 Changes in local (not in production):"
git log production..local --oneline
echo ""

# Ask for confirmation
read -p "❓ Do you want to merge these changes to production? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Merge cancelled"
    exit 1
fi

echo ""
echo "🔄 Merging local → production..."
echo ""

# Switch to production
git checkout production

# Merge from local
git merge local --no-ff -m "chore: sync tested changes from local

$(git log production..local --oneline)"

echo ""
echo "✅ Merge complete!"
echo ""

# Show current status
echo "📊 Production branch status:"
git log --oneline -5
echo ""

# Ask if user wants to tag
read -p "🏷️  Do you want to tag this release? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    read -p "Enter version (e.g., v1.2.0): " VERSION
    read -p "Enter release message: " MESSAGE
    git tag -a "$VERSION" -m "$MESSAGE"
    echo "✅ Tagged as $VERSION"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Deploy backend: gcloud run deploy ai-fitness-backend --source ."
echo "2. Deploy frontend: cd flutter_app && flutter build web --release && firebase deploy --only hosting"
echo "3. Switch back to local: git checkout local"
echo ""

# Ask if user wants to switch back
read -p "🔄 Switch back to local branch? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    git checkout local
    echo "✅ Switched to local branch"
else
    echo "📍 Staying on production branch"
fi

echo ""
echo "✅ Done!"

