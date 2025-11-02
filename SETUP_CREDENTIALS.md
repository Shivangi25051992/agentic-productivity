# 🔐 Firebase Credentials Setup Guide

## Current Issue

The backend cannot start because Firebase/Google Cloud credentials are not configured. You'll see this error:

```
google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found.
```

## Quick Fix (Choose One Option)

### ✅ Option 1: Firebase Service Account (Recommended)

**Best for:** Production-like local development

1. **Download Service Account Key:**
   - Go to [Firebase Console → Service Accounts](https://console.firebase.google.com/project/productivityai-mvp/settings/serviceaccounts/adminsdk)
   - Click **"Generate new private key"**
   - Save the JSON file (e.g., `firebase-service-account.json`) to your project root

2. **Update `.env.local`:**
   ```bash
   # Add this line with the actual path to your JSON file
   GOOGLE_APPLICATION_CREDENTIALS=/Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity/firebase-service-account.json
   ```

3. **Restart the backend:**
   ```bash
   ./stop-dev.sh
   ./start-dev.sh
   ```

---

### ✅ Option 2: gcloud CLI (Application Default Credentials)

**Best for:** If you already use gcloud for other projects

1. **Install gcloud CLI:**
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate:**
   ```bash
   gcloud auth login
   gcloud config set project productivityai-mvp
   gcloud auth application-default login
   ```

3. **Restart the backend:**
   ```bash
   ./stop-dev.sh
   ./start-dev.sh
   ```

---

### ✅ Option 3: Firebase Emulator (Local Testing Only)

**Best for:** Testing without real Firebase project

1. **Install Firebase CLI:**
   ```bash
   npm install -g firebase-tools
   ```

2. **Initialize Emulators:**
   ```bash
   cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
   firebase init emulators
   # Select: Firestore, Authentication
   ```

3. **Start Emulators (in a separate terminal):**
   ```bash
   firebase emulators:start
   ```

4. **Update `.env.local`:**
   ```bash
   # Add these lines
   FIRESTORE_EMULATOR_HOST=localhost:8080
   FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
   ```

5. **Restart the backend:**
   ```bash
   ./stop-dev.sh
   ./start-dev.sh
   ```

---

## Verification

Once credentials are set up, verify the backend starts successfully:

```bash
# Check backend health
curl http://localhost:8000/health

# Should return:
{"status":"healthy"}
```

---

## Current Configuration

Your `.env.local` file has been created with:

```bash
ENV=local
DEBUG=true
GOOGLE_CLOUD_PROJECT=productivityai-mvp
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars-long
```

**What's missing:** `GOOGLE_APPLICATION_CREDENTIALS` or Application Default Credentials

---

## Troubleshooting

### Error: "Your default credentials were not found"
- **Solution:** Follow Option 1 or Option 2 above

### Error: "Permission denied" when accessing Firestore
- **Solution:** Make sure your service account has "Cloud Datastore User" role
- Go to [IAM & Admin](https://console.cloud.google.com/iam-admin/iam?project=productivityai-mvp)
- Find your service account
- Add role: "Cloud Datastore User"

### Backend starts but can't connect to Firestore
- **Solution:** Check if the project ID is correct in `.env.local`
- Verify: `GOOGLE_CLOUD_PROJECT=productivityai-mvp`

---

## Security Notes

⚠️ **IMPORTANT:**

1. **Never commit** `firebase-service-account.json` to git
2. **Never commit** `.env.local` to git (already in `.gitignore`)
3. Change `ADMIN_PASSWORD` and `ADMIN_SECRET_KEY` before deploying to production
4. The current admin credentials are for local development only:
   - Username: `admin`
   - Password: `admin123`

---

## Next Steps

After setting up credentials:

1. ✅ Start the backend: `./start-dev.sh`
2. ✅ Test the enhanced onboarding flow at: http://localhost:8080
3. ✅ Access admin panel at: http://localhost:8000/admin
4. ✅ View API docs at: http://localhost:8000/docs

---

## Need Help?

If you're still having issues:

1. Check backend logs: `tail -f backend.log`
2. Check frontend logs: `tail -f frontend.log`
3. Verify `.env.local` exists and has correct values
4. Make sure you're using Python 3.11+: `python --version`
5. Make sure virtual environment is activated: `source .venv/bin/activate`



