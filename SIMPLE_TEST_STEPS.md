# 🧪 Simple Manual Test Steps

## ✅ Servers Status
- **Backend**: ✅ RUNNING on http://localhost:8000
- **Frontend**: ⏳ STARTING on http://localhost:8080 (wait 30 seconds)

---

## 📋 Test Steps (Copy these to Comet Browser)

### **STEP 1: Open App**
```
1. Open browser
2. Go to: http://localhost:8080
3. Wait for app to load (30 seconds first time)
4. You should see: Login or Signup screen
```

---

### **STEP 2: Sign Up**
```
1. Click "Sign Up" button
2. Fill form:
   - Email: test123@example.com
   - Password: TestPass123!
   - Name: Test User
3. Click "Sign Up"
4. Expected: Welcome screen or onboarding starts
```

---

### **STEP 3: Onboarding - Basic Info**
```
1. Enter:
   - Height: 170 cm
   - Weight: 70 kg
   - Age: 30
   - Gender: Male
2. Click "Next"
3. Expected: BMI result screen
```

---

### **STEP 4: BMI Result**
```
1. Check BMI is shown (should be ~24.2)
2. Click "Next"
3. Expected: Fitness goal screen
```

---

### **STEP 5: Select Goal**
```
1. Choose: "Lose Weight"
2. Click "Next"
3. Expected: Activity level screen
```

---

### **STEP 6: Activity Level**
```
1. Choose: "Moderately Active"
2. Click "Next"
3. Expected: Loading animation, then success screen
```

---

### **STEP 7: Dashboard**
```
1. Click "Get Started"
2. Expected: Dashboard with:
   - Calorie goal (e.g., 2000 kcal)
   - Activity rings (empty)
   - Bottom navigation
```

---

### **STEP 8: Log a Meal**
```
1. Tap "Assistant" in bottom navigation
2. Type: "2 eggs"
3. Click Send
4. Expected: 
   - Meal card shows "140 kcal"
   - AI says "2 eggs logged"
```

---

### **STEP 9: Check Dashboard**
```
1. Tap "Home" in bottom navigation
2. Expected:
   - Calories: 140 / 2000
   - Activity ring partially filled
   - Meal appears in timeline
```

---

### **STEP 10: Multi-Food**
```
1. Go back to "Assistant"
2. Type: "2 eggs, 1 bowl rice, 5 pistachios"
3. Click Send
4. Expected: 3 separate meal cards
```

---

## ✅ Success Criteria

- [ ] Signup works
- [ ] Onboarding completes
- [ ] Dashboard shows data
- [ ] Chat logs meals
- [ ] Dashboard updates
- [ ] Multi-food works
- [ ] No crashes
- [ ] No console errors

---

## 🐛 Report Issues

If something doesn't work, note:
1. Which step failed?
2. What error message?
3. Screenshot if possible
4. Check browser console (F12) for errors

---

## 📞 Quick Check

**Is app loading?**
```bash
# Check in terminal:
curl http://localhost:8080

# Should return HTML
```

**Is backend working?**
```bash
# Check in terminal:
curl http://localhost:8000/health

# Should return: {"status":"healthy",...}
```

---

**Ready to test!** Start from STEP 1 above. 🚀

