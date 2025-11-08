# 🚀 Fully Automated CI/CD Pipeline

**Your Release Manager & DevOps Engineer**

---

## 🎯 **What's Automated**

This system provides **end-to-end automated deployment** with:

1. ✅ **Auto-commit** to local branch
2. ✅ **Automated testing** (unit + integration + regression)
3. ✅ **Selective merge** to production (only differences)
4. ✅ **Configuration protection** (API keys, credentials untouched)
5. ✅ **Automated deployment** (backend + frontend)
6. ✅ **Post-deployment verification**
7. ✅ **Automatic rollback** on failure
8. ✅ **Zero-downtime** deployment

---

## 📦 **What's Included**

### **Main Scripts**:
1. **`deploy.sh`** - Master deployment script (Release Manager)
2. **`test_regression.py`** - Regression testing suite
3. **`manage_config.sh`** - Configuration management
4. **`merge_to_production.sh`** - Manual merge helper

### **Features**:
- ✅ Automated testing before deployment
- ✅ Backup before every deployment
- ✅ Rollback on failure
- ✅ Configuration protection
- ✅ Sensitive file exclusion
- ✅ Post-deployment verification

---

## 🚀 **Quick Start**

### **One Command Deployment**:
```bash
./deploy.sh
```

That's it! The script will:
1. Commit your changes to `local`
2. Run all tests
3. Merge to `production` (only safe files)
4. Deploy to production
5. Verify deployment
6. Rollback if anything fails

---

## 📋 **Detailed Workflow**

### **Step 1: Pre-flight Checks** ✅
- Verify git repository
- Check current branch
- Ensure backend/frontend running
- Validate production branch exists

### **Step 2: Commit to Local** ✅
- Stage all changes
- Generate timestamped commit message
- Commit to `local` branch

### **Step 3: Automated Testing** ✅
- Backend unit tests
- Backend integration tests
- API health checks
- Frontend analysis

### **Step 4: Regression Testing** ✅
- Test critical user flows
- Chat endpoint (context-aware responses)
- Timeline endpoint
- Task creation
- Profile endpoints

### **Step 5: Backup Production** ✅
- Create backup tag
- Tag format: `backup-YYYYMMDD-HHMMSS`
- Enables instant rollback

### **Step 6: Merge to Production** ✅
- Get list of changed files
- **Exclude sensitive files**:
  - `.env`, `.env.*`
  - `*.key`, `*.pem`
  - `*credentials*`
  - `*secret*`
  - Firebase admin SDK files
- Merge only safe files
- Create release tag

### **Step 7: Deploy** ✅
- Deploy backend to Cloud Run
- Build Flutter web
- Deploy frontend to Firebase Hosting

### **Step 8: Verify Deployment** ✅
- Backend health check
- Test critical endpoints
- Check for errors in logs

### **Step 9: Rollback (if needed)** ✅
- Automatically triggered on failure
- Revert to backup tag
- Re-deploy previous version

### **Step 10: Cleanup** ✅
- Switch back to `local` branch
- Remove old backup tags (keep last 5)

---

## 🔐 **Configuration Protection**

### **Sensitive Files (NEVER Deployed)**:
```
.env
.env.local
.env.production
*.key
*.pem
*credentials*.json
*secret*
firebase-adminsdk-*.json
```

### **How It Works**:
1. Script automatically excludes these patterns
2. Only code changes are deployed
3. Configurations remain untouched
4. API keys and credentials safe

### **Manage Configurations**:
```bash
./manage_config.sh
```

This will:
- Check for sensitive files in git
- Update .gitignore
- Create .env.template
- Verify config files exist

---

## 🧪 **Testing**

### **Run Tests Manually**:
```bash
# Regression tests
./test_regression.py

# All tests (if you have pytest)
pytest tests/ -v
```

### **Skip Tests** (not recommended):
```bash
./deploy.sh --skip-tests
```

---

## 🔄 **Rollback**

### **Automatic Rollback**:
- Triggered automatically on deployment failure
- Reverts to last backup tag
- Re-deploys previous version

### **Manual Rollback**:
```bash
# 1. List backup tags
git tag -l "backup-*"

# 2. Switch to production
git checkout production

# 3. Revert to backup
git reset --hard backup-YYYYMMDD-HHMMSS

# 4. Re-deploy
gcloud run deploy ai-fitness-backend --source .
cd flutter_app && flutter build web --release && firebase deploy --only hosting
```

---

## 📊 **Monitoring**

### **Check Deployment Status**:
```bash
# Backend logs
gcloud run services logs read ai-fitness-backend --limit 50

# Frontend logs
firebase hosting:logs

# Git history
git log production --oneline -10
```

### **View Backup Tags**:
```bash
git tag -l "backup-*" | sort -r | head -5
```

---

## 🎯 **Usage Examples**

### **Example 1: Normal Deployment**
```bash
# Make changes on local branch
git checkout local
# ... make changes ...

# Deploy (auto-commit, test, merge, deploy)
./deploy.sh

# Output:
# ✅ Pre-flight checks passed
# ✅ Changes committed to local branch
# ✅ All tests passed
# ✅ Regression tests passed
# ✅ Production backed up as tag: backup-20251103-143022
# ✅ Changes merged to production (tag: v20251103-143025)
# ✅ Deployment completed
# ✅ Deployment verification passed
# ✅ All steps completed successfully
```

### **Example 2: Deployment with Test Failure**
```bash
./deploy.sh

# Output:
# ✅ Pre-flight checks passed
# ✅ Changes committed to local branch
# ❌ Backend unit tests failed
# ❌ Tests failed! Aborting deployment.
# (No changes deployed)
```

### **Example 3: Deployment with Rollback**
```bash
./deploy.sh

# Output:
# ✅ Pre-flight checks passed
# ✅ All tests passed
# ✅ Production backed up
# ✅ Changes merged to production
# ✅ Deployment completed
# ❌ Backend health check failed after deployment
# ❌ Deployment failed! Rolling back...
# ✅ Rollback completed
```

---

## 🛠️ **Configuration**

### **Edit deploy.sh**:
```bash
# Backend URL
BACKEND_URL="http://localhost:8000"

# Frontend URL
FRONTEND_URL="http://localhost:9090"

# Skip tests (not recommended)
SKIP_TESTS=false

# Force deployment (skip confirmations)
FORCE_DEPLOY=false
```

### **Add Custom Tests**:
Edit `test_regression.py` to add your tests:
```python
def test_my_feature(self):
    """Test my new feature"""
    response = requests.get(f"{BACKEND_URL}/my-endpoint")
    assert response.status_code == 200
    self.passed += 1
```

---

## 📋 **Checklist Before First Deployment**

### **Setup** (One-time):
- [ ] Run `./manage_config.sh` to protect sensitive files
- [ ] Create `.env.local` with local credentials
- [ ] Create `.env.production` with production credentials
- [ ] Configure `gcloud` CLI for Cloud Run
- [ ] Configure `firebase` CLI for Hosting
- [ ] Update `deploy.sh` with your project details

### **Before Each Deployment**:
- [ ] Test locally (http://localhost:9090)
- [ ] Commit changes to `local` branch (or let script do it)
- [ ] Run `./deploy.sh`
- [ ] Monitor deployment
- [ ] Verify production

---

## 🚨 **Troubleshooting**

### **Issue: Tests Failing**
```bash
# Run tests manually to see details
./test_regression.py

# Fix issues, then deploy again
./deploy.sh
```

### **Issue: Deployment Failed**
```bash
# Check logs
tail -50 deploy.log

# Rollback manually if needed
git checkout production
git reset --hard backup-YYYYMMDD-HHMMSS
```

### **Issue: Sensitive Files in Git**
```bash
# Remove from git (keep local copy)
git rm --cached .env
git commit -m "Remove sensitive file"

# Run config management
./manage_config.sh
```

---

## 💡 **Best Practices**

### **DO**:
- ✅ Always test locally first
- ✅ Let the script handle deployment
- ✅ Review backup tags regularly
- ✅ Monitor post-deployment
- ✅ Keep configurations separate

### **DON'T**:
- ❌ Skip tests (unless emergency)
- ❌ Commit sensitive files
- ❌ Deploy directly to production
- ❌ Force push to production
- ❌ Delete backup tags

---

## 📊 **Summary**

**Automated Pipeline**:
```
Local Changes → Auto-Commit → Tests → Regression → Backup → 
Merge (safe files only) → Deploy → Verify → Success/Rollback
```

**Safety Features**:
- ✅ Automated testing
- ✅ Configuration protection
- ✅ Backup before deployment
- ✅ Automatic rollback
- ✅ Post-deployment verification

**Time Savings**:
- Manual: 30-45 minutes
- Automated: 5-10 minutes
- **Savings**: 70-85% faster

---

## 🚀 **Ready to Deploy!**

### **First Deployment**:
```bash
# 1. Setup (one-time)
./manage_config.sh

# 2. Deploy
./deploy.sh

# 3. Monitor
# Watch the output for any issues
```

### **Daily Deployments**:
```bash
# Just run this command
./deploy.sh
```

---

**Your automated Release Manager & DevOps Engineer is ready!** 🎉

**Questions?** Check the scripts or documentation.  
**Issues?** The script will handle rollback automatically.  
**Success?** Enjoy your automated deployments! 🚀

