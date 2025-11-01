# AI Productivity App

An AI-powered fitness and task tracking application with natural language input, built with FastAPI (backend) and Flutter (frontend).

## Features

- 🤖 **Natural Language Input**: Chat-based interface for logging meals, workouts, and tasks
- 🍽️ **Fitness Tracking**: Automatic calorie estimation and meal logging
- ✅ **Task Management**: AI-powered task creation and tracking
- 📊 **Analytics Dashboard**: Visual insights into your fitness and productivity
- 🔔 **Smart Reminders**: Notifications for tasks and fitness goals
- 🔐 **Firebase Authentication**: Secure user authentication with email/password and Google Sign-In
- 👨‍💼 **Admin Panel**: Beautiful admin dashboard for configuration management

## Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- Google Cloud Firestore
- Firebase Admin SDK
- OpenAI API / Google Gemini
- Uvicorn ASGI server

**Frontend:**
- Flutter (Web, iOS, Android)
- Provider (State Management)
- Firebase Auth & Firestore
- Material Design 3

## Quick Start

### Prerequisites

- Python 3.11+
- Flutter SDK
- Firebase project with Firestore enabled
- OpenAI API key or Google Gemini API key
- Google Cloud service account JSON

### One-Command Setup

**Start both backend and frontend:**
```bash
./start-dev.sh
```

This will:
- ✅ Start FastAPI backend on http://localhost:8000
- ✅ Start Flutter frontend (Chrome by default)
- ✅ Check dependencies and environment
- ✅ Show live logs

**Stop all servers:**
```bash
./stop-dev.sh
```

### Manual Setup

#### Backend Setup

1. **Create virtual environment:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env.local
# Edit .env.local with your credentials:
# - GOOGLE_APPLICATION_CREDENTIALS (path to service account JSON)
# - GOOGLE_CLOUD_PROJECT
# - OPENAI_API_KEY or GEMINI_API_KEY
# - ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_SECRET_KEY
```

4. **Start backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access:**
   - API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - API Docs: http://localhost:8000/docs

#### Frontend Setup

1. **Install Flutter dependencies:**
```bash
cd flutter_app
flutter pub get
```

2. **Configure Firebase:**
```bash
# Install FlutterFire CLI
dart pub global activate flutterfire_cli

# Configure Firebase for your project
flutterfire configure
```

3. **Run Flutter app:**
```bash
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

For Android emulator, use:
```bash
flutter run -d <device-id> --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

## Test Credentials

**User Account:**
- Email: `tester@example.com`
- Password: `Test1234!`

**Admin Panel:**
- Username: Set in `.env.local` as `ADMIN_USERNAME`
- Password: Set in `.env.local` as `ADMIN_PASSWORD`

## Usage

### Chat Interface

Type natural language commands in the chat:

**Meals:**
- "Lunch: chicken bowl 200g"
- "Breakfast: 2 eggs and toast"
- "Dinner: salmon with rice 300g"

**Workouts:**
- "Ran 5km in 30 minutes"
- "Gym session: bench press 3 sets"
- "Yoga for 45 minutes"

**Tasks:**
- "Remind me to call John tomorrow"
- "Add task: finish report by Friday"
- "Meeting with team at 3pm"

### Admin Panel

1. Navigate to http://localhost:8000/admin
2. Login with admin credentials
3. Configure:
   - AI Services (OpenAI/Gemini API keys)
   - Google Cloud credentials
   - Firebase configuration
   - SMTP settings
   - LLM prompt template
4. Test configurations before saving

## Project Structure

```
agentic-productivity/
├── app/                          # FastAPI backend
│   ├── main.py                  # Main application & /chat endpoint
│   ├── models/                  # Pydantic models
│   ├── routers/                 # API endpoints
│   ├── services/                # Business logic
│   ├── core/                    # Configuration
│   └── static/admin/            # Admin panel UI
├── flutter_app/                 # Flutter frontend
│   ├── lib/
│   │   ├── main.dart           # App entry point
│   │   ├── screens/            # UI screens
│   │   ├── widgets/            # Reusable widgets
│   │   ├── services/           # API & Firebase services
│   │   ├── providers/          # State management
│   │   ├── models/             # Data models
│   │   └── utils/              # Utilities & theme
│   └── pubspec.yaml            # Flutter dependencies
├── docs/                        # Documentation
├── .env.example                 # Environment template
├── .env.local                   # Local environment (gitignored)
├── requirements.txt             # Python dependencies
├── start-dev.sh                 # Start all servers
├── stop-dev.sh                  # Stop all servers
└── README.md                    # This file
```

## API Endpoints

### Public Endpoints

- `POST /chat` - Natural language input processing
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login

### Protected Endpoints (Require Firebase Auth)

**Tasks:**
- `GET /tasks` - List user tasks
- `POST /tasks/create` - Create task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task

**Fitness:**
- `GET /fitness/logs` - List fitness logs
- `POST /fitness/log` - Log meal/workout
- `GET /fitness/stats` - Get statistics

**User:**
- `GET /users/me` - Get current user
- `PUT /users/me` - Update profile

### Admin Endpoints (Require Admin Auth)

- `POST /admin/login` - Admin login
- `GET /admin/config/active` - Get active configuration
- `POST /admin/config` - Save new configuration
- `PUT /admin/config/{id}` - Update configuration

## Development

### Backend Development

**Run with auto-reload:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**View logs:**
```bash
tail -f backend.log
```

**Test API:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input":"Lunch: chicken bowl 200g","type":"auto"}'
```

### Frontend Development

**Hot reload:**
- Press `r` in Flutter terminal for hot reload
- Press `R` for hot restart
- Press `q` to quit

**View logs:**
```bash
tail -f frontend.log
```

**Debug:**
- Open Chrome DevTools (F12)
- Check Console for errors
- Network tab for API calls

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'email_validator'"**
```bash
pip install "pydantic[email]"
```

**"google.auth.exceptions.DefaultCredentialsError"**
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to valid service account JSON
- Check `GOOGLE_CLOUD_PROJECT` is set correctly

**"403 Missing or insufficient permissions"**
- Grant `roles/datastore.user` to your service account in Google Cloud Console
- Enable Firestore API

**"400 The query requires an index"**
- Click the link in the error message to create the index in Firebase Console

### Frontend Issues

**"Connection refused" or "Failed to send"**
- Ensure backend is running on port 8000
- Check `API_BASE_URL` in Flutter run command

**"There are multiple heroes that share the same tag"**
- Fixed in latest code; do a hot restart (R)

**"FirebaseOptions cannot be null"**
- Run `flutterfire configure` to generate Firebase config
- Ensure `firebase_options.dart` exists

**Blank white page on web**
- Check browser console for errors
- Ensure Firebase is initialized correctly

## Deployment

### Backend (Google Cloud Run)

1. **Build Docker image:**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-productivity-api
```

2. **Deploy:**
```bash
gcloud run deploy ai-productivity-api \
  --image gcr.io/YOUR_PROJECT_ID/ai-productivity-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. **Set environment variables in Cloud Run console**

### Frontend (Firebase Hosting)

1. **Build for web:**
```bash
cd flutter_app
flutter build web
```

2. **Deploy:**
```bash
firebase init hosting
firebase deploy --only hosting
```

### Mobile Apps

**Android:**
```bash
flutter build apk --release
# Upload to Google Play Console
```

**iOS:**
```bash
flutter build ios --release
# Use Xcode to archive and upload to App Store Connect
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check the [Documentation](docs/index.md)
- Review [Setup Guide](docs/setup.md)
- Open an issue on GitHub

## Changelog

### v0.1.0 (MVP)
- ✅ Natural language chat interface
- ✅ AI-powered meal/workout/task logging
- ✅ Calorie estimation
- ✅ Firebase authentication
- ✅ Admin configuration panel
- ✅ Cross-platform Flutter app
- ✅ Real-time dashboard updates
- ✅ One-click dev environment setup
