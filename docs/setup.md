# Setup Guide

## Quick Start (Recommended) 🚀

**One command to start everything:**
```bash
./start-dev.sh
```

This automatically:
- ✅ Starts FastAPI backend on http://localhost:8000
- ✅ Starts Flutter frontend
- ✅ Checks all dependencies
- ✅ Shows live logs

**To stop all servers:**
```bash
./stop-dev.sh
```

---

## Manual Setup

### Prerequisites
- Python 3.11+
- Flutter SDK
- Google Cloud project + service account (for Firestore)
- Firebase project
- OpenAI or Gemini API key

### Backend Setup

**1) Create virtual environment:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**2) Configure environment:**
```bash
cp .env.example .env.local
# Edit .env.local with your credentials
```

Required environment variables:
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON
- `GOOGLE_CLOUD_PROJECT` - Your GCP project ID
- `OPENAI_API_KEY` or `GEMINI_API_KEY` - AI service API key
- `ADMIN_USERNAME` - Admin panel username
- `ADMIN_PASSWORD` - Admin panel password
- `ADMIN_SECRET_KEY` - JWT secret for admin auth

**3) Start backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**4) Access:**
- API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- API Docs: http://localhost:8000/docs

### Frontend Setup

**1) Install Flutter dependencies:**
```bash
cd flutter_app
flutter pub get
```

**2) Configure Firebase:**
```bash
# Install FlutterFire CLI
dart pub global activate flutterfire_cli

# Configure Firebase
flutterfire configure
```

**3) Run Flutter app:**
```bash
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

For Android emulator:
```bash
flutter run -d <device-id> --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

---

## Test Credentials

**User Account:**
- Email: `tester@example.com`
- Password: `Test1234!`

**Admin Panel:**
- Username: Set in `.env.local` as `ADMIN_USERNAME`
- Password: Set in `.env.local` as `ADMIN_PASSWORD`

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
./stop-dev.sh  # or manually: kill -9 $(lsof -t -i:8000)
```

**Missing dependencies:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Firestore permission errors:**
- Enable Firestore API in Google Cloud Console
- Grant `roles/datastore.user` to your service account

### Frontend Issues

**Connection refused:**
- Ensure backend is running on port 8000
- Check API_BASE_URL in flutter run command

**Firebase not initialized:**
```bash
cd flutter_app
flutterfire configure
```

---

## Next Steps

1. ✅ Start servers with `./start-dev.sh`
2. ✅ Login with test credentials
3. ✅ Configure admin panel (http://localhost:8000/admin)
4. ✅ Test chat interface: "Lunch: chicken bowl 200g"
5. ✅ Check dashboard for logged data

For more details, see [README.md](../README.md)
