# 🚀 CI/CD Setup Guide

## Overview

This project uses **GitHub Actions** for automated deployment to Google Cloud and Firebase.

### Deployment Flow:
```
Git Push → GitHub Actions → Tests → Deploy Backend → Deploy Frontend → Deploy Firestore
```

---

## 🔧 Setup Instructions

### Step 1: Create GitHub Repository

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity

# Initialize git (if not already)
git init

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/agentic-productivity.git

# Add all files
git add .

# Commit
git commit -m "feat: Initial commit with CI/CD pipeline"

# Push to main
git push -u origin main
```

---

### Step 2: Set Up Google Cloud Service Account

1. **Create Service Account**:
```bash
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions" \
  --project=productivityai-mvp
```

2. **Grant Permissions**:
```bash
gcloud projects add-iam-policy-binding productivityai-mvp \
  --member="serviceAccount:github-actions@productivityai-mvp.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding productivityai-mvp \
  --member="serviceAccount:github-actions@productivityai-mvp.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding productivityai-mvp \
  --member="serviceAccount:github-actions@productivityai-mvp.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

3. **Create Key**:
```bash
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@productivityai-mvp.iam.gserviceaccount.com
```

4. **Copy the key content** (you'll need it for GitHub Secrets)

---

### Step 3: Set Up Firebase Service Account

1. Go to: https://console.firebase.google.com/project/productivityai-mvp/settings/serviceaccounts/adminsdk

2. Click "Generate new private key"

3. Save the JSON file

---

### Step 4: Add GitHub Secrets

Go to: https://github.com/YOUR_USERNAME/agentic-productivity/settings/secrets/actions

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GCP_SA_KEY` | Content of `github-actions-key.json` | Google Cloud service account |
| `FIREBASE_SERVICE_ACCOUNT` | Content of Firebase service account JSON | Firebase admin SDK |
| `FIREBASE_TOKEN` | Run `firebase login:ci` | Firebase CLI token |
| `OPENAI_API_KEY` | Your OpenAI API key | For AI features |

---

### Step 5: Enable GitHub Actions

1. Go to: https://github.com/YOUR_USERNAME/agentic-productivity/actions

2. Enable workflows

3. The workflow will run automatically on every push to `main`

---

## 📋 Workflow Stages

### 1. Test Stage
- ✅ Runs Python backend tests
- ✅ Runs Flutter tests
- ✅ Validates code quality

### 2. Deploy Backend
- ✅ Builds Docker container
- ✅ Deploys to Google Cloud Run
- ✅ Sets environment variables
- ✅ Configures auto-scaling

### 3. Deploy Frontend
- ✅ Builds Flutter web app
- ✅ Updates API URL
- ✅ Deploys to Firebase Hosting
- ✅ Invalidates CDN cache

### 4. Deploy Firestore
- ✅ Deploys security rules
- ✅ Deploys composite indexes
- ✅ Validates configuration

### 5. Notify
- ✅ Sends deployment status
- ✅ Provides URLs

---

## 🔄 Local vs Cloud Sync

### Problem We're Solving:
- ❌ Local changes not in sync with cloud
- ❌ Manual deployments error-prone
- ❌ No version control for deployments

### Solution:
- ✅ All deployments go through GitHub
- ✅ Git is single source of truth
- ✅ Automated testing before deploy
- ✅ Rollback capability via Git

---

## 🚀 Deployment Commands

### Local Development:
```bash
# Start local environment
./deploy_local.sh

# Make changes
# ... edit code ...

# Test locally
python test_logging_local.py

# Stop local
./stop_local.sh
```

### Deploy to Production:
```bash
# Commit changes
git add .
git commit -m "feat: Your feature description"

# Push to GitHub (triggers CI/CD)
git push origin main

# GitHub Actions will:
# 1. Run tests
# 2. Deploy backend
# 3. Deploy frontend
# 4. Deploy Firestore
```

---

## 📊 Monitoring Deployments

### GitHub Actions Dashboard:
https://github.com/YOUR_USERNAME/agentic-productivity/actions

### View Logs:
```bash
# Backend logs
gcloud run services logs read aiproductivity-backend \
  --project=productivityai-mvp \
  --region=us-central1 \
  --limit=100

# Frontend (Firebase Hosting)
# View in Firebase Console
```

---

## 🔙 Rollback

### If Deployment Fails:

1. **Revert Git Commit**:
```bash
git revert HEAD
git push origin main
```

2. **Or Deploy Previous Version**:
```bash
# Find previous commit
git log --oneline

# Deploy specific commit
git checkout <commit-hash>
git push origin main --force
```

3. **Or Manual Rollback**:
```bash
# Backend
gcloud run services update-traffic aiproductivity-backend \
  --to-revisions=PREVIOUS_REVISION=100 \
  --project=productivityai-mvp \
  --region=us-central1

# Frontend
# Use Firebase Console to rollback
```

---

## 🧪 Testing Before Deployment

### Required Tests:
```bash
# 1. Local tests
./deploy_local.sh
python test_logging_local.py

# 2. Backend tests
pytest tests/

# 3. Flutter tests
cd flutter_app
flutter test

# 4. Integration tests
# ... add your integration tests ...
```

---

## 📝 Best Practices

### 1. Branch Strategy
```
main (production) ← Only deploy from here
  ↑
develop (staging) ← Test here first
  ↑
feature/* (development) ← Work here
```

### 2. Commit Messages
```bash
# Good
git commit -m "feat: Add landing page"
git commit -m "fix: Resolve routing issue"
git commit -m "docs: Update deployment guide"

# Bad
git commit -m "changes"
git commit -m "fix"
```

### 3. Pre-Deployment Checklist
- [ ] Tests pass locally
- [ ] Code reviewed
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Documentation updated

---

## 🔐 Security

### Secrets Management:
- ✅ Never commit `.env` files
- ✅ Use GitHub Secrets for sensitive data
- ✅ Rotate service account keys regularly
- ✅ Use least-privilege IAM roles

### Firestore Rules:
- ✅ Always deploy with security rules
- ✅ Test rules before deploying
- ✅ Never allow public write access

---

## 🎯 Summary

### Old Way (Manual):
```bash
./auto_deploy.sh  # Manual, error-prone
```

### New Way (Automated):
```bash
git push origin main  # Automated, tested, versioned
```

### Benefits:
- ✅ **Version Control**: Every deployment is tracked
- ✅ **Automated Testing**: Catches bugs before production
- ✅ **Consistent**: Same process every time
- ✅ **Rollback**: Easy to revert if needed
- ✅ **Audit Trail**: See who deployed what and when

---

**Now your deployments are automated, tested, and versioned! 🎉**

