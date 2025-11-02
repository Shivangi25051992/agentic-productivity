# 🚀 FIRESTORE MIGRATION PLAN
## From Flat Collections to Subcollection-Based Architecture

**Date**: November 2, 2025  
**Estimated Duration**: 2-3 weeks  
**Risk Level**: Medium (requires careful data migration)

---

## 📋 MIGRATION OVERVIEW

### **Current State**
```
firestore/
├── users/{userId}
├── tasks/{taskId}
├── fitness_logs/{logId}
├── chat_history/{messageId}
└── food_database/{foodId}
```

### **Target State**
```
firestore/
├── users/{userId}
│   ├── profile/current
│   ├── daily_stats/{date}
│   ├── fitness_logs/{logId}
│   ├── tasks/{taskId}
│   ├── chat_sessions/{sessionId}
│   │   └── messages/{messageId}
│   ├── preferences/current
│   └── achievements/{achievementId}
└── food_database/{foodId}
```

---

## 🎯 PHASE 1: PREPARATION (Days 1-2)

### **Step 1.1: Backup Current Data**
```bash
# Export all collections
gcloud firestore export gs://productivityai-mvp-backups/$(date +%Y%m%d) \
  --project=productivityai-mvp

# Verify backup
gsutil ls gs://productivityai-mvp-backups/
```

### **Step 1.2: Create Migration Scripts**
Create Python scripts for data migration:

```python
# migrate_users.py
def migrate_user_data(user_id):
    """Migrate one user's data to new structure"""
    
    # 1. Create user profile subcollection
    old_user = db.collection('users').document(user_id).get()
    new_profile = {
        'fitnessGoal': old_user.get('fitness_goal'),
        'dailyCalorieGoal': old_user.get('daily_calorie_goal'),
        'preferences': {
            'preferredFoods': old_user.get('preferred_foods', []),
            'dislikedFoods': old_user.get('disliked_foods', [])
        },
        'updatedAt': firestore.SERVER_TIMESTAMP
    }
    db.collection('users').document(user_id)\
      .collection('profile').document('current').set(new_profile)
    
    # 2. Migrate fitness logs
    old_logs = db.collection('fitness_logs')\
                  .where('user_id', '==', user_id).stream()
    
    for log in old_logs:
        data = log.to_dict()
        new_log = transform_fitness_log(data)
        db.collection('users').document(user_id)\
          .collection('fitness_logs').document(log.id).set(new_log)
    
    # 3. Migrate tasks
    old_tasks = db.collection('tasks')\
                   .where('user_id', '==', user_id).stream()
    
    for task in old_tasks:
        data = task.to_dict()
        new_task = transform_task(data)
        db.collection('users').document(user_id)\
          .collection('tasks').document(task.id).set(new_task)
    
    # 4. Migrate chat history
    migrate_chat_history(user_id)
    
    # 5. Generate daily stats
    generate_daily_stats(user_id)
```

### **Step 1.3: Deploy New Indexes**
```json
// firestore.indexes.json (updated)
{
  "indexes": [
    {
      "collectionGroup": "fitness_logs",
      "queryScope": "COLLECTION_GROUP",
      "fields": [
        {"fieldPath": "date", "order": "DESCENDING"},
        {"fieldPath": "timestamp", "order": "DESCENDING"}
      ]
    },
    {
      "collectionGroup": "fitness_logs",
      "queryScope": "COLLECTION_GROUP",
      "fields": [
        {"fieldPath": "logType", "order": "ASCENDING"},
        {"fieldPath": "timestamp", "order": "DESCENDING"}
      ]
    },
    {
      "collectionGroup": "tasks",
      "queryScope": "COLLECTION_GROUP",
      "fields": [
        {"fieldPath": "status", "order": "ASCENDING"},
        {"fieldPath": "dueDate", "order": "ASCENDING"}
      ]
    },
    {
      "collectionGroup": "daily_stats",
      "queryScope": "COLLECTION_GROUP",
      "fields": [
        {"fieldPath": "date", "order": "DESCENDING"}
      ]
    }
  ]
}
```

```bash
firebase deploy --only firestore:indexes --project productivityai-mvp
```

---

## 🔄 PHASE 2: MIGRATION EXECUTION (Days 3-7)

### **Step 2.1: Test Migration on Single User**
```python
# Test with one user first
test_user_id = "alice_test_user_id"
migrate_user_data(test_user_id)

# Verify data integrity
verify_migration(test_user_id)
```

### **Step 2.2: Batch Migration (Small Batches)**
```python
# Migrate users in batches of 100
def migrate_all_users():
    users = db.collection('users').stream()
    batch_size = 100
    batch = []
    
    for user in users:
        batch.append(user.id)
        
        if len(batch) >= batch_size:
            # Process batch
            for user_id in batch:
                try:
                    migrate_user_data(user_id)
                    print(f"✅ Migrated {user_id}")
                except Exception as e:
                    print(f"❌ Failed {user_id}: {e}")
                    # Log to error collection for retry
                    log_migration_error(user_id, str(e))
            
            batch = []
            time.sleep(5)  # Rate limiting
    
    # Process remaining
    for user_id in batch:
        migrate_user_data(user_id)
```

### **Step 2.3: Update Backend Code**
Update all backend services to use new structure:

```python
# OLD
db.collection('fitness_logs').where('user_id', '==', user_id).get()

# NEW
db.collection('users').document(user_id)\
  .collection('fitness_logs').order_by('timestamp', 'DESC').get()
```

**Files to Update**:
- `app/services/database.py` - All CRUD operations
- `app/main.py` - Chat endpoint, fitness logging
- `app/routers/fitness.py` - Fitness endpoints
- `app/routers/profile.py` - Profile endpoints
- `app/services/chat_history_service.py` - Chat history

### **Step 2.4: Update Frontend Code**
Update Flutter app to use new API structure:

```dart
// OLD
api.get('/fitness-logs?user_id=$userId')

// NEW (backend handles subcollection internally)
api.get('/fitness-logs')  // Backend uses auth.uid automatically
```

---

## 🧪 PHASE 3: TESTING & VALIDATION (Days 8-10)

### **Step 3.1: Data Integrity Checks**
```python
def verify_migration(user_id):
    """Verify all data migrated correctly"""
    
    # Check profile
    profile = db.collection('users').document(user_id)\
                .collection('profile').document('current').get()
    assert profile.exists, "Profile not migrated"
    
    # Check fitness logs count
    old_count = len(list(db.collection('fitness_logs')
                        .where('user_id', '==', user_id).stream()))
    new_count = len(list(db.collection('users').document(user_id)
                        .collection('fitness_logs').stream()))
    assert old_count == new_count, f"Log count mismatch: {old_count} vs {new_count}"
    
    # Check tasks count
    old_tasks = len(list(db.collection('tasks')
                        .where('user_id', '==', user_id).stream()))
    new_tasks = len(list(db.collection('users').document(user_id)
                        .collection('tasks').stream()))
    assert old_tasks == new_tasks, f"Task count mismatch"
    
    # Check daily stats generated
    stats = db.collection('users').document(user_id)\
              .collection('daily_stats').limit(1).get()
    assert len(stats) > 0, "Daily stats not generated"
    
    print(f"✅ {user_id} migration verified")
```

### **Step 3.2: Performance Testing**
```python
import time

def test_query_performance():
    """Compare old vs new query performance"""
    
    user_id = "test_user"
    
    # OLD: Query across all users
    start = time.time()
    old_logs = db.collection('fitness_logs')\
                 .where('user_id', '==', user_id)\
                 .order_by('timestamp', 'DESC')\
                 .limit(50).get()
    old_time = time.time() - start
    
    # NEW: Query within user subcollection
    start = time.time()
    new_logs = db.collection('users').document(user_id)\
                 .collection('fitness_logs')\
                 .order_by('timestamp', 'DESC')\
                 .limit(50).get()
    new_time = time.time() - start
    
    print(f"OLD: {old_time:.3f}s, NEW: {new_time:.3f}s")
    print(f"Improvement: {((old_time - new_time) / old_time * 100):.1f}%")
```

### **Step 3.3: User Acceptance Testing**
- Test with 5-10 real users
- Verify all features work
- Check data accuracy
- Monitor for errors

---

## 🚀 PHASE 4: DEPLOYMENT (Days 11-14)

### **Step 4.1: Deploy Backend Changes**
```bash
# Deploy updated backend
cd /Users/pchintanwar/Documents/Projects-AIProductivity/agentic-productivity
git add .
git commit -m "feat: migrate to subcollection-based architecture"
git push origin main

# Deploy to production (if using Cloud Run/App Engine)
gcloud app deploy
```

### **Step 4.2: Deploy Frontend Changes**
```bash
# Build and deploy Flutter web app
cd flutter_app
flutter build web --release
firebase deploy --only hosting
```

### **Step 4.3: Update Security Rules**
```javascript
// firestore.rules (updated for subcollections)
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // User root document
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
      
      // Profile subcollection
      match /profile/{document} {
        allow read, write: if request.auth.uid == userId;
      }
      
      // Daily stats subcollection
      match /daily_stats/{date} {
        allow read: if request.auth.uid == userId;
        allow write: if request.auth.uid == userId;
      }
      
      // Fitness logs subcollection
      match /fitness_logs/{logId} {
        allow read, create, update, delete: if request.auth.uid == userId;
      }
      
      // Tasks subcollection
      match /tasks/{taskId} {
        allow read, create, update, delete: if request.auth.uid == userId;
      }
      
      // Chat sessions subcollection
      match /chat_sessions/{sessionId} {
        allow read, create, update, delete: if request.auth.uid == userId;
        
        // Messages within session
        match /messages/{messageId} {
          allow read, create, delete: if request.auth.uid == userId;
        }
      }
      
      // Achievements subcollection (read-only for users)
      match /achievements/{achievementId} {
        allow read: if request.auth.uid == userId;
        allow write: if false;  // Backend only
      }
    }
    
    // Food database (global, read-only)
    match /food_database/{foodId} {
      allow read: if request.auth != null;
      allow write: if false;  // Backend only
    }
  }
}
```

```bash
firebase deploy --only firestore:rules
```

---

## 🧹 PHASE 5: CLEANUP (Days 15-21)

### **Step 5.1: Verify All Users Migrated**
```python
def check_migration_status():
    """Check which users are migrated"""
    
    all_users = db.collection('users').stream()
    migrated = 0
    not_migrated = []
    
    for user in all_users:
        profile = db.collection('users').document(user.id)\
                    .collection('profile').document('current').get()
        
        if profile.exists:
            migrated += 1
        else:
            not_migrated.append(user.id)
    
    print(f"✅ Migrated: {migrated}")
    print(f"❌ Not migrated: {len(not_migrated)}")
    
    if not_migrated:
        print("Users to retry:", not_migrated[:10])
```

### **Step 5.2: Delete Old Collections (After 1 Week)**
```python
# ONLY after confirming everything works!
def cleanup_old_collections():
    """Delete old flat collections"""
    
    print("⚠️  WARNING: This will delete old collections!")
    print("⚠️  Make sure new structure is working!")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("Cancelled")
        return
    
    # Delete old collections
    delete_collection(db.collection('tasks'), batch_size=500)
    delete_collection(db.collection('fitness_logs'), batch_size=500)
    delete_collection(db.collection('chat_history'), batch_size=500)
    
    print("✅ Old collections deleted")

def delete_collection(coll_ref, batch_size):
    """Delete collection in batches"""
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0
    
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    
    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)
    
    print(f"Deleted {deleted} documents from {coll_ref.id}")
```

---

## 📊 ROLLBACK PLAN

If migration fails:

### **Step 1: Stop Migration**
```python
# Set flag to stop migration
db.collection('_system').document('migration').set({
    'status': 'paused',
    'reason': 'Critical error detected'
})
```

### **Step 2: Restore from Backup**
```bash
# Restore from backup
gcloud firestore import gs://productivityai-mvp-backups/20251102 \
  --project=productivityai-mvp
```

### **Step 3: Revert Code**
```bash
git revert HEAD
git push origin main
```

---

## ✅ SUCCESS CRITERIA

Migration is successful when:

- [ ] All users migrated (100%)
- [ ] Data integrity verified (0 discrepancies)
- [ ] Query performance improved (>30% faster)
- [ ] No user-reported issues for 1 week
- [ ] All automated tests passing
- [ ] Security rules working correctly
- [ ] Old collections deleted

---

## 📈 EXPECTED BENEFITS

### **Performance**
- **Query Speed**: 30-50% faster (no cross-user filtering)
- **Dashboard Load**: 70% faster (denormalized daily_stats)
- **Scalability**: Linear scaling to millions of users

### **Security**
- **Data Isolation**: Perfect user isolation
- **GDPR Compliance**: Easy user data deletion
- **Security Rules**: Simpler and more maintainable

### **Developer Experience**
- **Code Simplicity**: No user_id filtering needed
- **Testing**: Easier to test with isolated data
- **Debugging**: Clearer data structure

---

## 🚨 RISKS & MITIGATION

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data loss during migration | High | Low | Full backup before migration |
| Downtime during deployment | Medium | Medium | Blue-green deployment |
| Performance degradation | Medium | Low | Load testing before production |
| User confusion | Low | Medium | Clear communication, gradual rollout |
| Migration script bugs | High | Medium | Test on single user first |

---

**Next Steps**:
1. Review and approve this plan
2. Schedule migration window
3. Create backup
4. Execute Phase 1

**Estimated Completion**: November 23, 2025

