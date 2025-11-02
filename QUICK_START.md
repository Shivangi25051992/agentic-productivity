# 🚀 Quick Start Guide

## Your App is LIVE! 🎉

### 🌐 Access Your App
**Web**: https://productivityai-mvp.web.app

### 📱 Test on iPhone
1. Open Safari: https://productivityai-mvp.web.app
2. Tap Share → "Add to Home Screen"
3. Use as native app!

---

## 🔄 Deploy Updates (One Command)

```bash
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
./auto_deploy.sh
```

That's it! This will:
- Build & deploy backend
- Build & deploy frontend
- Update Firestore rules

---

## 🧪 Test Features

### 1. Sign Up
- Go to https://productivityai-mvp.web.app
- Create account with email/password
- You'll receive notification at: shivganga25shingatwar@gmail.com

### 2. Chat Assistant
- Type: "I ate 2 eggs and banana for breakfast"
- AI will parse and log the meal
- Check timeline to see it logged

### 3. Submit Feedback
- Click floating button (bottom-right)
- Add screenshot + comments
- You'll get email notification

### 4. Wipe Data
- Go to Settings
- Tap "Wipe All My Logs"
- Confirm deletion

---

## 📊 Monitor Your App

### Backend Logs
```bash
gcloud logs tail --project=productivityai-mvp
```

### Firestore Console
https://console.firebase.google.com/project/productivityai-mvp/firestore

### Cloud Run Console
https://console.cloud.google.com/run?project=productivityai-mvp

---

## 🐛 If Something Breaks

### Redeploy Everything
```bash
./auto_deploy.sh
```

### Backend Only
```bash
gcloud run deploy aiproductivity-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --project productivityai-mvp
```

### Frontend Only
```bash
cd flutter_app
flutter build web
firebase deploy --only hosting
```

---

## 💡 Tips

1. **Test on real device** - iOS Safari works best
2. **Use feedback button** - I get notified instantly
3. **Check email** - All signups notify you
4. **Monitor costs** - Check OpenAI usage dashboard

---

## 📧 Support

**Admin Email**: shivganga25shingatwar@gmail.com
- New signups → Email notification
- Feedback → Email with screenshot
- Errors → (Coming soon with logging)

---

## 🎯 What's Working

✅ Signup with email/password  
✅ AI chat assistant  
✅ Meal logging & classification  
✅ Timeline view  
✅ Feedback system  
✅ Wipe all logs  
✅ Invitation notifications  

---

## 🔜 Coming Soon

⏳ Admin dashboard for KPIs  
⏳ Cost tracking  
⏳ Production logging  
⏳ Performance monitoring  

---

**Your app is production-ready! Start testing! 🚀**
