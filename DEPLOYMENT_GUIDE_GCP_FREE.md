# 🚀 Deployment Guide - Google Cloud Free Tier

**Goal**: Deploy to free Google Cloud with custom domain for testing  
**Cost**: $0/month (Free tier)  
**Timeline**: 2-3 hours

---

## 📋 Google Cloud Free Tier Includes

### **Always Free Resources**:
- ✅ Cloud Run: 2 million requests/month
- ✅ Cloud Firestore: 1GB storage, 50K reads/day
- ✅ Cloud Functions: 2 million invocations/month
- ✅ Cloud Build: 120 build-minutes/day
- ✅ Firebase Hosting: 10GB storage, 360MB/day transfer
- ✅ Custom domain (via Firebase Hosting)

**Perfect for testing with 10-100 users!**

---

## 🎯 Architecture

```
┌─────────────────────────────────────────────┐
│  Frontend (Firebase Hosting)                │
│  • Flutter Web                              │
│  • Custom Domain: app.yourdomain.com        │
│  • Free SSL Certificate                     │
│  • Global CDN                               │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Backend (Cloud Run)                        │
│  • FastAPI                                  │
│  • Auto-scaling (0-1 instances)             │
│  • Custom Domain: api.yourdomain.com        │
│  • Free SSL Certificate                     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Database (Firestore)                       │
│  • Native mode                              │
│  • Automatic backups                        │
│  • Free tier: 1GB, 50K reads/day            │
└─────────────────────────────────────────────┘
```

---

## 🚀 Step-by-Step Deployment

### **Phase 1: Setup Google Cloud Project** (10 mins)

1. **Create/Select Project**:
   ```bash
   gcloud projects create aiproductivity-test --name="AI Productivity Test"
   gcloud config set project aiproductivity-test
   ```

2. **Enable Required APIs**:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable firestore.googleapis.com
   gcloud services enable firebase.googleapis.com
   ```

3. **Set up Billing** (Required but won't be charged in free tier):
   ```bash
   # Link billing account (you won't be charged within free tier limits)
   gcloud beta billing accounts list
   gcloud beta billing projects link aiproductivity-test \
     --billing-account=YOUR_BILLING_ACCOUNT_ID
   ```

---

### **Phase 2: Deploy Backend to Cloud Run** (20 mins)

1. **Create Dockerfile** (if not exists):
   ```dockerfile
   # Dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application
   COPY app ./app
   COPY .env.local .env
   
   # Expose port
   EXPOSE 8080
   
   # Run application
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

2. **Build and Deploy**:
   ```bash
   # Build container
   gcloud builds submit --tag gcr.io/aiproductivity-test/backend
   
   # Deploy to Cloud Run
   gcloud run deploy aiproductivity-backend \
     --image gcr.io/aiproductivity-test/backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="OPENAI_API_KEY=${OPENAI_API_KEY}" \
     --set-env-vars="GOOGLE_CLOUD_PROJECT=aiproductivity-test" \
     --set-env-vars="FIREBASE_API_KEY=${FIREBASE_API_KEY}" \
     --max-instances=1 \
     --memory=512Mi \
     --cpu=1 \
     --timeout=60s
   ```

3. **Get Backend URL**:
   ```bash
   gcloud run services describe aiproductivity-backend \
     --region us-central1 \
     --format='value(status.url)'
   ```
   
   Example output: `https://aiproductivity-backend-xxxxx-uc.a.run.app`

---

### **Phase 3: Deploy Frontend to Firebase Hosting** (15 mins)

1. **Build Flutter Web**:
   ```bash
   cd flutter_app
   flutter build web --release
   ```

2. **Initialize Firebase Hosting**:
   ```bash
   firebase init hosting
   
   # Select options:
   # - Use existing project: aiproductivity-test
   # - Public directory: build/web
   # - Single-page app: Yes
   # - GitHub integration: No (for now)
   ```

3. **Update API URL in Flutter**:
   ```dart
   // lib/utils/constants.dart
   class AppConstants {
     static const String apiBaseUrl = 
       'https://aiproductivity-backend-xxxxx-uc.a.run.app';
   }
   ```

4. **Rebuild and Deploy**:
   ```bash
   flutter build web --release
   firebase deploy --only hosting
   ```

5. **Get Frontend URL**:
   ```
   https://aiproductivity-test.web.app
   ```

---

### **Phase 4: Setup Custom Domain** (30 mins)

#### **Option A: Free Domain (Recommended for Testing)**

Use **Freenom** or **Cloudflare** for free domain:

1. **Get Free Domain**:
   - Go to https://www.freenom.com
   - Register: `aiproductivity-test.tk` (free for 12 months)

2. **Add to Firebase Hosting**:
   ```bash
   firebase hosting:channel:deploy production
   
   # In Firebase Console:
   # Hosting > Add custom domain
   # Enter: aiproductivity-test.tk
   # Follow DNS setup instructions
   ```

3. **Update DNS Records**:
   ```
   A Record: @ → 151.101.1.195
   A Record: @ → 151.101.65.195
   TXT Record: @ → [verification code from Firebase]
   ```

#### **Option B: Use Firebase Free Subdomain**

Just use: `https://aiproductivity-test.web.app` (instant, free, SSL included)

---

### **Phase 5: Mobile Testing Setup** (20 mins)

#### **1. Build Android APK**:
```bash
cd flutter_app

# Build debug APK for testing
flutter build apk --debug

# Output: build/app/outputs/flutter-apk/app-debug.apk
```

#### **2. Build iOS (Mac only)**:
```bash
# Build iOS app
flutter build ios --debug

# Or use TestFlight for distribution
flutter build ipa
```

#### **3. Distribute for Testing**:

**Option A: Direct APK Download**:
```bash
# Upload APK to Firebase Hosting
cp build/app/outputs/flutter-apk/app-debug.apk flutter_app/build/web/downloads/
firebase deploy --only hosting

# Share link: https://aiproductivity-test.web.app/downloads/app-debug.apk
```

**Option B: Firebase App Distribution** (Recommended):
```bash
# Install Firebase CLI tools
npm install -g firebase-tools

# Deploy to App Distribution
firebase appdistribution:distribute \
  build/app/outputs/flutter-apk/app-debug.apk \
  --app YOUR_FIREBASE_APP_ID \
  --groups testers \
  --release-notes "Initial test build"
```

**Option C: Google Play Internal Testing** (Best for iOS + Android):
```bash
# Build release APK
flutter build apk --release

# Upload to Google Play Console > Internal Testing
# Add testers via email
# They get instant access via Play Store
```

---

## 📱 Mobile Testing Instructions

### **For Testers**:

**Android**:
1. Download APK from link
2. Enable "Install from Unknown Sources"
3. Install and test

**iOS** (TestFlight):
1. Install TestFlight app from App Store
2. Open invitation link
3. Install beta app

---

## 💰 Cost Monitoring

### **Set Up Budget Alerts**:

```bash
# Create budget alert
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="AI Productivity Test Budget" \
  --budget-amount=10USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

### **Monitor Usage**:

```bash
# Check Cloud Run usage
gcloud run services describe aiproductivity-backend \
  --region us-central1 \
  --format='value(status.traffic)'

# Check Firestore usage
gcloud firestore operations list

# View costs
gcloud billing accounts list
```

---

## 🔒 Security Setup

### **1. Enable CORS**:
```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aiproductivity-test.web.app",
        "https://aiproductivity-test.tk",  # Your custom domain
        "http://localhost:3000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **2. Set Up API Keys**:
```bash
# Store secrets in Google Secret Manager
echo -n "$OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-
echo -n "$FIREBASE_API_KEY" | gcloud secrets create firebase-api-key --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding openai-api-key \
  --member=serviceAccount:YOUR_SERVICE_ACCOUNT \
  --role=roles/secretmanager.secretAccessor
```

### **3. Enable Firestore Security Rules**:
```bash
firebase deploy --only firestore:rules
```

---

## 🧪 Testing Checklist

### **Before Sharing with Testers**:

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Custom domain working (if using)
- [ ] SSL certificates active
- [ ] API endpoints responding
- [ ] Firebase Auth working
- [ ] Firestore rules deployed
- [ ] Mobile APK built and tested
- [ ] Budget alerts configured
- [ ] Error monitoring setup (Sentry)

### **Test Scenarios**:

1. **Signup/Login** ✅
   - New user registration
   - Existing user login
   - Token refresh

2. **Chat Functionality** ✅
   - Send messages
   - Receive AI responses
   - Chat history persists

3. **Meal Logging** ✅
   - Single item meals
   - Multi-item meals (no duplicates)
   - Timeline display

4. **Mobile Specific** ✅
   - Touch interactions
   - Keyboard behavior
   - Offline handling
   - Push notifications (if enabled)

---

## 📊 Monitoring & Analytics

### **1. Setup Cloud Monitoring**:
```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com

# Create uptime check
gcloud monitoring uptime-checks create \
  --display-name="Backend Health Check" \
  --resource-type=uptime-url \
  --host=aiproductivity-backend-xxxxx-uc.a.run.app \
  --path=/health
```

### **2. Setup Error Tracking**:
```python
# Install Sentry
pip install sentry-sdk[fastapi]

# app/main.py
import sentry_sdk
sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    environment="production",
    traces_sample_rate=0.1,
)
```

### **3. Setup Analytics**:
```dart
// Flutter: Google Analytics
import 'package:firebase_analytics/firebase_analytics.dart';

final analytics = FirebaseAnalytics.instance;
analytics.logEvent(name: 'meal_logged', parameters: {'type': 'breakfast'});
```

---

## 🚀 Deployment Commands (Quick Reference)

```bash
# Deploy everything
./deploy.sh

# Or manually:
# 1. Deploy backend
gcloud run deploy aiproductivity-backend --source .

# 2. Deploy frontend
cd flutter_app && flutter build web && firebase deploy --only hosting

# 3. Deploy Firestore rules
firebase deploy --only firestore:rules,firestore:indexes

# 4. Deploy Cloud Functions
firebase deploy --only functions
```

---

## 📱 Share with Testers

### **Email Template**:

```
Subject: AI Productivity App - Beta Testing Invitation

Hi [Tester Name],

You're invited to test our AI-powered fitness & productivity app!

🌐 Web App: https://aiproductivity-test.web.app
📱 Android APK: [Download Link]
🍎 iOS TestFlight: [Invitation Link]

Test Credentials:
Email: test1@aiproductivity.app
Password: Test@123

Please test:
✅ Signup/Login
✅ Chat with AI assistant
✅ Log meals (try: "I had oatmeal with banana for breakfast")
✅ Check timeline
✅ Mobile experience

Report issues: [Google Form / GitHub Issues]

Thanks for testing!
```

---

## 🎯 Success Metrics

**After 1 Week**:
- [ ] 10+ test users active
- [ ] 100+ meals logged
- [ ] 500+ chat messages
- [ ] <1% error rate
- [ ] <2s average response time
- [ ] $0 spent (within free tier)

---

## 🔄 CI/CD Setup (Bonus)

### **GitHub Actions for Auto-Deploy**:

```yaml
# .github/workflows/deploy.yml
name: Deploy to GCP

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: aiproductivity-backend
          region: us-central1
          source: .
          
      - name: Deploy to Firebase Hosting
        run: |
          cd flutter_app
          flutter build web
          firebase deploy --only hosting
```

---

**Ready to deploy?** Let me create the deployment scripts! 🚀

