# 🔌 DEDICATED PORTS - AI Productivity Fitness App

**Reserved Ports**: To avoid conflicts with other applications

---

## 📊 PORT ALLOCATION:

### Backend (FastAPI):
```
Port: 8000
URL: http://localhost:8000
Status: ✅ Running
```

### Frontend (Flutter Web):
```
Port: 9090
URL: http://localhost:9090
Status: 🔄 Starting
```

---

## 🚫 PORTS TO AVOID:

- **8080**: Used by other JS application (dashboard)
- **3000**: Common for React/Node apps
- **5000**: Common for Flask apps
- **4200**: Common for Angular apps

---

## ✅ WHY THESE PORTS:

- **8000**: Standard for FastAPI/Python backends
- **9090**: Uncommon, unlikely to conflict

---

## 🌐 ACCESS YOUR APP:

### Local Development:
```
Frontend: http://localhost:9090
Backend:  http://localhost:8000
```

### Health Check:
```bash
curl http://localhost:8000/health
```

---

## 🔧 TO CHANGE PORTS (If Needed):

### Backend:
```bash
# Edit command to use different port
uvicorn main:app --reload --host 0.0.0.0 --port XXXX
```

### Frontend:
```bash
# Edit command to use different port
flutter run -d chrome --web-port XXXX
```

---

**Your app will be at: http://localhost:9090** 🚀

