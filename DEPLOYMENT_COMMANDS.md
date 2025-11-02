# 🚀 Deployment Commands

## Quick Commands

### Local Deployment
```bash
./deploy_local.sh
```

### Cloud Deployment
```bash
./deploy_cloud.sh
```

### Stop Local Services
```bash
./stop_local.sh
```

---

## 📋 Local Deployment (`deploy_local.sh`)

### What It Does:
1. ✅ Clears ports 8000 (backend) and 3000 (frontend)
2. ✅ Starts backend with auto-reload
3. ✅ Starts Flutter web frontend
4. ✅ Runs automated tests
5. ✅ Shows logs and service URLs

### Usage:
```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
./deploy_local.sh
```

### Output:
```
🚀 LOCAL DEPLOYMENT STARTING

Step 1/5: Checking Ports
✅ Ports cleared

Step 2/5: Starting Backend
✅ Backend started successfully (PID: 12345)
   URL: http://localhost:8000
   Logs: backend_local.log

Step 3/5: Starting Frontend
✅ Frontend started (PID: 12346)
   URL: http://localhost:3000
   Logs: frontend_local.log

Step 4/5: Running Automated Tests
🧪 Running test suite...

Step 5/5: Deployment Summary
🎉 LOCAL DEPLOYMENT COMPLETE!

📊 SERVICES RUNNING
🔧 Backend: http://localhost:8000
🌐 Frontend: http://localhost:3000
```

### Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Logs:
```bash
# View backend logs
tail -f backend_local.log

# View frontend logs
tail -f frontend_local.log

# View both
tail -f backend_local.log frontend_local.log
```

### Stop Services:
```bash
./stop_local.sh
```

---

## ☁️ Cloud Deployment (`deploy_cloud.sh`)

### What It Does:
1. ✅ Builds and deploys backend to Google Cloud Run
2. ✅ Updates frontend API configuration
3. ✅ Builds Flutter web app
4. ✅ Deploys frontend to Firebase Hosting
5. ✅ Deploys Firestore rules and indexes

### Usage:
```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
./deploy_cloud.sh
```

### Output:
```
☁️  CLOUD DEPLOYMENT STARTING

Step 1/4: Deploying Backend to Cloud Run
✅ Backend deployed: https://aiproductivity-backend-rhwrraai2a-uc.a.run.app

Step 2/4: Updating Frontend Configuration
✅ API URL updated in Flutter

Step 3/4: Building Flutter Web
✅ Flutter web built successfully

Step 4/4: Deploying Frontend to Firebase
✅ Frontend deployed: https://productivityai-mvp.web.app

Step 5/5: Deploying Firestore Rules & Indexes
✅ Firestore rules deployed

🎉 DEPLOYMENT COMPLETE!

🌐 Frontend URL: https://productivityai-mvp.web.app
🔧 Backend URL: https://aiproductivity-backend-rhwrraai2a-uc.a.run.app
```

### Access:
- **Frontend**: https://productivityai-mvp.web.app
- **Backend API**: https://aiproductivity-backend-rhwrraai2a-uc.a.run.app
- **API Docs**: https://aiproductivity-backend-rhwrraai2a-uc.a.run.app/docs

### Monitor:
```bash
# View Cloud Run logs
gcloud run services logs read aiproductivity-backend \
  --project=productivityai-mvp \
  --region=us-central1 \
  --limit=100

# View Firestore
https://console.firebase.google.com/project/productivityai-mvp/firestore

# View Cloud Run
https://console.cloud.google.com/run?project=productivityai-mvp
```

---

## 🛑 Stop Local Services (`stop_local.sh`)

### What It Does:
1. ✅ Stops backend process
2. ✅ Stops frontend process
3. ✅ Cleans up ports
4. ✅ Removes PID files

### Usage:
```bash
./stop_local.sh
```

### Output:
```
🛑 STOPPING LOCAL SERVICES

🔴 Stopping backend (PID: 12345)...
✅ Backend stopped

🔴 Stopping frontend (PID: 12346)...
✅ Frontend stopped

🧹 Cleaning up ports...

✅ All local services stopped!
```

---

## 🔄 Workflow Examples

### Development Workflow
```bash
# 1. Start local environment
./deploy_local.sh

# 2. Make code changes
# ... edit files ...

# 3. Backend auto-reloads, frontend needs manual refresh
# Press 'r' in Flutter console to hot reload

# 4. Test changes
# Open http://localhost:3000

# 5. Stop when done
./stop_local.sh
```

### Testing Workflow
```bash
# 1. Deploy locally
./deploy_local.sh

# 2. Run tests (automatically runs during deploy)
# Or manually:
python test_logging_local.py

# 3. Fix any issues
# ... edit code ...

# 4. Re-test
python test_logging_local.py

# 5. Deploy to cloud when tests pass
./deploy_cloud.sh
```

### Production Deployment Workflow
```bash
# 1. Test locally first
./deploy_local.sh
# ... test thoroughly ...
./stop_local.sh

# 2. Deploy to cloud
./deploy_cloud.sh

# 3. Monitor logs
gcloud run services logs read aiproductivity-backend \
  --project=productivityai-mvp \
  --region=us-central1 \
  --limit=100 \
  --format="table(timestamp, textPayload)"

# 4. Test production
# Open https://productivityai-mvp.web.app
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill processes manually
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Or use stop script
./stop_local.sh
```

### Backend Won't Start
```bash
# Check logs
cat backend_local.log

# Common issues:
# - Missing dependencies: pip install -r requirements.txt
# - Port in use: ./stop_local.sh
# - Environment variables: check .env.local
```

### Frontend Won't Start
```bash
# Check logs
cat frontend_local.log

# Common issues:
# - Flutter not installed: flutter doctor
# - Dependencies missing: cd flutter_app && flutter pub get
# - Port in use: ./stop_local.sh
```

### Cloud Deployment Fails
```bash
# Check if gcloud is configured
gcloud config list

# Check if firebase is logged in
firebase login

# Check project
gcloud config get-value project
# Should be: productivityai-mvp
```

---

## 📊 Comparison

| Feature | Local | Cloud |
|---------|-------|-------|
| **Speed** | Fast (seconds) | Slow (minutes) |
| **Cost** | Free | ~$5-10/month |
| **Testing** | Easy | Harder |
| **Auto-reload** | Yes (backend) | No |
| **Public Access** | No | Yes |
| **Production Ready** | No | Yes |
| **Logs** | Local files | Cloud Logging |
| **Database** | Shared Firestore | Shared Firestore |

---

## 🎯 Best Practices

### When to Use Local
- ✅ Development and testing
- ✅ Debugging issues
- ✅ Rapid iteration
- ✅ Before deploying to cloud

### When to Use Cloud
- ✅ Production deployment
- ✅ Sharing with users
- ✅ Testing on real devices
- ✅ Final testing before release

### Recommended Flow
1. **Develop locally** with `./deploy_local.sh`
2. **Test locally** with automated tests
3. **Fix issues** found in tests
4. **Deploy to cloud** with `./deploy_cloud.sh`
5. **Monitor** Cloud Run logs
6. **Test production** with real users

---

## 📝 Summary

```bash
# Local development
./deploy_local.sh    # Start local environment
./stop_local.sh      # Stop local environment

# Cloud deployment
./deploy_cloud.sh    # Deploy to production
```

**That's it! Two simple commands for all your deployment needs! 🚀**

