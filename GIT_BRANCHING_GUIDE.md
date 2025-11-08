# 🌿 Git Branching Strategy - Local & Production

**Date**: November 3, 2025  
**Purpose**: Separate development and production code for safe, incremental deployments

---

## 🎯 **Branch Structure**

```
main (protected - never deploy directly)
├── local (development & testing)
└── production (production-ready code only)
```

### **Branch Purposes**:

| Branch | Purpose | When to Use |
|--------|---------|-------------|
| `main` | Protected baseline | Never touch directly |
| `local` | Development & testing | All new features, fixes, experiments |
| `production` | Production-ready code | Only tested, approved changes |

---

## 📊 **Current State**

### **Local Branch** (Development):
```bash
Commit: 70f8b6a5
Message: "feat: Chat response fix + Timeline performance + Collapsible sections + setState fixes"

Contains:
- ✅ Chat response generator (NEW)
- ✅ Timeline performance optimizations
- ✅ Collapsible sections
- ✅ setState() fixes
- ✅ All documentation
- ✅ Test scripts
```

### **Production Branch** (Stable):
```bash
Commit: 68a78884
Message: "fix: CORS configuration already includes localhost:9090"

Contains:
- ✅ Basic app functionality
- ✅ CORS configuration
- ✅ Local development setup
- ❌ Missing: Today's new features
```

### **Difference**:
- Local is **3 commits ahead** of production
- Local has **51 files changed** (9,484 insertions)

---

## 🔄 **Workflow**

### **Daily Development Cycle**:

```
1. Work on `local` branch
   ↓
2. Test locally (localhost)
   ↓
3. Commit to `local`
   ↓
4. Merge `local` → `production` (selective)
   ↓
5. Deploy from `production`
   ↓
6. Tag release
```

---

## 🚀 **How to Merge Local → Production**

### **Option A: Merge All Changes** (Full Sync)

Use when: All local changes are tested and ready for production

```bash
# 1. Switch to production branch
git checkout production

# 2. Merge all changes from local
git merge local --no-ff -m "chore: sync local changes to production"

# 3. Verify
git log --oneline -5

# 4. Push to remote (if needed)
git push origin production
```

---

### **Option B: Cherry-Pick Specific Commits** (Selective)

Use when: Only some commits are ready for production

```bash
# 1. Switch to production branch
git checkout production

# 2. View local commits
git log local --oneline -10

# 3. Cherry-pick specific commits
git cherry-pick 70f8b6a5  # Today's features
git cherry-pick 4c77fb77  # Documentation

# 4. Verify
git log --oneline -5
```

---

### **Option C: Cherry-Pick Specific Files** (Most Granular)

Use when: Only specific files are ready for production

```bash
# 1. Switch to production branch
git checkout production

# 2. Check out specific files from local
git checkout local -- app/services/chat_response_generator.py
git checkout local -- app/main.py
git checkout local -- flutter_app/lib/providers/timeline_provider.dart

# 3. Commit the changes
git add app/services/chat_response_generator.py app/main.py flutter_app/lib/providers/timeline_provider.dart
git commit -m "feat: add chat response generator and timeline optimizations"

# 4. Verify
git status
```

---

## 📝 **Today's Deployment Plan**

### **Files Ready for Production** (Tested ✅):

#### **Backend** (4 files):
```bash
app/main.py                                    # Chat response integration
app/services/chat_response_generator.py        # NEW FILE
app/services/database.py                       # Query optimizations
app/routers/timeline.py                        # NEW FILE - Timeline endpoint
```

#### **Frontend** (6 files):
```bash
flutter_app/lib/providers/timeline_provider.dart
flutter_app/lib/screens/chat/chat_screen.dart
flutter_app/lib/screens/timeline/timeline_screen.dart
flutter_app/lib/screens/timeline/widgets/timeline_section_header.dart
flutter_app/lib/screens/timeline/widgets/timeline_item.dart
flutter_app/lib/models/timeline_activity.dart
```

#### **Configuration** (1 file):
```bash
firestore.indexes.json                         # Composite indexes
```

---

### **Step-by-Step: Merge Today's Changes**

```bash
# 1. Switch to production branch
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
git checkout production

# 2. Check out ONLY production-ready files from local
# Backend files
git checkout local -- app/main.py
git checkout local -- app/services/chat_response_generator.py
git checkout local -- app/services/database.py
git checkout local -- app/routers/timeline.py

# Frontend files
git checkout local -- flutter_app/lib/providers/timeline_provider.dart
git checkout local -- flutter_app/lib/screens/chat/chat_screen.dart
git checkout local -- flutter_app/lib/screens/timeline/
git checkout local -- flutter_app/lib/models/timeline_activity.dart

# Configuration
git checkout local -- firestore.indexes.json

# 3. Stage the changes
git add app/ flutter_app/lib/ firestore.indexes.json

# 4. Commit to production
git commit -m "feat: Add chat response generator, timeline optimizations, and collapsible sections

- Add context-aware chat response generator
- Optimize timeline performance (debouncing, RepaintBoundary)
- Add collapsible date sections
- Fix setState() errors
- Add unified timeline endpoint

Tested: All features tested locally
Risk: Low
Rollback: Available via git revert"

# 5. Tag the release
git tag -a v1.2.0 -m "Chat response fix + Timeline performance + Collapsible sections"

# 6. Verify what's in production now
git log --oneline -3

# 7. Switch back to local for continued development
git checkout local
```

---

## 🔍 **Verification Commands**

### **Compare Branches**:
```bash
# See what's different between local and production
git diff production..local --name-only

# See detailed diff
git diff production..local

# See commit differences
git log production..local --oneline
```

### **Check Current Branch**:
```bash
git branch  # Shows current branch with *
```

### **View Branch History**:
```bash
git log --oneline --graph --all --decorate
```

---

## 🛡️ **Safety Rules**

### **DO**:
- ✅ Always work on `local` branch
- ✅ Test thoroughly before merging to `production`
- ✅ Commit frequently to `local`
- ✅ Tag releases on `production`
- ✅ Keep `production` clean (only tested code)

### **DON'T**:
- ❌ Never work directly on `production`
- ❌ Never merge untested code to `production`
- ❌ Never force push to `production`
- ❌ Never delete `production` branch
- ❌ Never commit directly to `main`

---

## 📋 **Common Commands**

### **Switch Branches**:
```bash
git checkout local       # Switch to local
git checkout production  # Switch to production
```

### **See What's Changed**:
```bash
git status              # Current changes
git diff                # Detailed diff
git log --oneline -10   # Recent commits
```

### **Undo Changes** (if needed):
```bash
# Undo uncommitted changes
git restore <file>

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

---

## 🎯 **Deployment Workflow**

### **Full Workflow** (Local → Production → Deploy):

```bash
# 1. Develop on local
git checkout local
# ... make changes ...
git add .
git commit -m "feat: new feature"

# 2. Test locally
./start_local.sh
# ... test in browser ...

# 3. Merge to production (selective)
git checkout production
git checkout local -- path/to/file.py
git commit -m "feat: deploy new feature"

# 4. Tag release
git tag -a v1.2.1 -m "New feature"

# 5. Deploy backend
gcloud run deploy ai-fitness-backend --source .

# 6. Deploy frontend
cd flutter_app
flutter build web --release
firebase deploy --only hosting

# 7. Switch back to local
git checkout local
```

---

## 📊 **Branch Status Dashboard**

### **Check Status Anytime**:
```bash
#!/bin/bash
# Save as: check_branch_status.sh

echo "=== GIT BRANCH STATUS ==="
echo ""
echo "Current Branch:"
git branch --show-current
echo ""
echo "Local Branch (last 3 commits):"
git log local --oneline -3
echo ""
echo "Production Branch (last 3 commits):"
git log production --oneline -3
echo ""
echo "Differences (local vs production):"
git log production..local --oneline
echo ""
echo "Files changed:"
git diff production..local --name-only | wc -l
```

---

## 🚀 **Ready to Merge?**

### **Quick Command** (for today's changes):

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
git checkout production
git checkout local -- app/main.py app/services/chat_response_generator.py app/services/database.py app/routers/timeline.py flutter_app/lib/providers/timeline_provider.dart flutter_app/lib/screens/chat/chat_screen.dart flutter_app/lib/screens/timeline/ flutter_app/lib/models/timeline_activity.dart firestore.indexes.json
git add app/ flutter_app/lib/ firestore.indexes.json
git commit -m "feat: Chat response + Timeline optimizations + Collapsible sections"
git tag -a v1.2.0 -m "Production release: Nov 3, 2025"
git checkout local
```

---

## 💡 **Summary**

**Branching Strategy**:
- `local` = development (all changes)
- `production` = stable (tested changes only)

**Workflow**:
1. Develop on `local`
2. Test locally
3. Merge to `production` (selective)
4. Deploy from `production`
5. Tag release

**Benefits**:
- ✅ Safe deployments
- ✅ Easy rollback
- ✅ Clear separation
- ✅ Incremental updates

**Ready to merge when you are!** 🚀

