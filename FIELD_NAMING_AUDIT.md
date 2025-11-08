# 🔍 FIELD NAMING AUDIT & FIX PLAN

## 📊 ROOT CAUSE ANALYSIS

### Critical Issue: Field Naming Inconsistency
**Problem**: The application has a fundamental inconsistency between `camelCase` (frontend) and `snake_case` (backend/Firestore).

**Impact**:
- ❌ Firestore queries fail (500 errors)
- ❌ Indexes don't match actual field names
- ❌ Data not displayed in UI
- ❌ Timeline shows incorrect times
- ❌ Dashboard shows no activities

---

## 🎯 AFFECTED AREAS

### 1. Tasks Collection
**Current State**:
- Frontend expects: `dueDate` (camelCase)
- Backend queries: `due_date` (snake_case)
- Firestore index: `dueDate` (wrong!) → Should be `due_date`
- Actual data in Firestore: **UNKNOWN** (need to check)

**Fields to Audit**:
- `task_id` vs `taskId`
- `user_id` vs `userId`
- `due_date` vs `dueDate`
- `created_at` vs `createdAt`
- `updated_at` vs `updatedAt`

### 2. Fitness Logs Collection
**Current State**:
- Backend uses: `log_type`, `timestamp`, `user_id`, `log_id`
- Frontend expects: Same (mostly snake_case in models)
- Firestore indexes: Match backend

**Fields to Audit**:
- `log_id` vs `logId`
- `user_id` vs `userId`
- `log_type` vs `logType`
- `ai_parsed_data` vs `aiParsedData`

### 3. User Profiles Collection
**Current State**:
- Backend uses: `user_id`, `created_at`, `updated_at`
- Frontend: Mostly consistent

**Fields to Audit**:
- `user_id` vs `userId`
- `created_at` vs `createdAt`
- `updated_at` vs `updatedAt`

---

## 🔧 RECOMMENDED FIX STRATEGY

### Option A: Standardize on snake_case (RECOMMENDED)
**Why**: 
- ✅ Python/FastAPI convention
- ✅ Firestore best practice
- ✅ Most backend code already uses this
- ✅ Easier to maintain consistency

**Changes Required**:
1. Update Firestore indexes to use `snake_case`
2. Ensure all backend models use `snake_case`
3. Update frontend models to map `snake_case` ↔ `camelCase`
4. Verify actual Firestore data uses `snake_case`

### Option B: Standardize on camelCase
**Why**:
- ❌ Requires more backend changes
- ❌ Goes against Python conventions
- ❌ More error-prone

**Verdict**: Use Option A (snake_case)

---

## 📋 ACTION PLAN

### Phase 1: Audit Firestore Data (5 min)
**Goal**: Understand what field names are ACTUALLY stored in Firestore

**Steps**:
1. Query `tasks` collection - check 1 document
2. Query `fitness_logs` collection - check 1 document
3. Query `user_profiles` collection - check 1 document
4. Document actual field names

**Script**: Create `audit_firestore_fields.py`

### Phase 2: Fix Firestore Indexes (2 min)
**Goal**: Ensure indexes match actual field names

**Files to Update**:
- `firestore.indexes.json` - Already updated to `due_date` ✅

**Deploy**:
```bash
firebase deploy --only firestore:indexes
```

### Phase 3: Fix Backend Models (10 min)
**Goal**: Ensure all backend code uses `snake_case` consistently

**Files to Check**:
- `app/models.py` - Task, FitnessLog, User models
- `app/services/database.py` - Query field names
- `app/routers/*.py` - Request/response models

**Verification**:
- Search for `dueDate` → Should be `due_date`
- Search for `logType` → Should be `log_type`
- Search for `userId` → Should be `user_id`

### Phase 4: Fix Frontend Models (15 min)
**Goal**: Ensure frontend models properly map between conventions

**Files to Update**:
- `flutter_app/lib/models/task.dart`
- `flutter_app/lib/models/fitness_log.dart`
- `flutter_app/lib/models/user.dart`

**Pattern**:
```dart
class TaskModel {
  final String taskId;
  final String dueDate; // camelCase for Dart
  
  factory TaskModel.fromJson(Map<String, dynamic> json) {
    return TaskModel(
      taskId: json['task_id'], // Map from snake_case
      dueDate: json['due_date'], // Map from snake_case
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'task_id': taskId, // Map to snake_case
      'due_date': dueDate, // Map to snake_case
    };
  }
}
```

### Phase 5: Test Complete Flow (10 min)
**Goal**: Verify everything works end-to-end

**Test Cases**:
1. ✅ Sign up new user
2. ✅ Create task via chat
3. ✅ Log meal via chat
4. ✅ View dashboard - tasks appear
5. ✅ View dashboard - meals appear
6. ✅ View timeline - correct times
7. ✅ No 500 errors in console

---

## 🚨 CRITICAL FINDINGS

### Issue 1: Tasks Query Failure
**Error**: `GET /tasks/?start_due=2025-11-03T00:00:00.000 500`

**Root Cause**: 
- Frontend sends `start_due` parameter
- Backend queries `due_date >= start_due`
- Firestore index expects `due_date` field
- But if data has `dueDate`, query fails

**Fix**: Ensure data uses `due_date` (snake_case)

### Issue 2: Insights Query Failure
**Error**: `GET /insights 500`

**Root Cause**: Similar composite index issue with fitness_logs

**Fix**: Ensure indexes match actual field names

### Issue 3: Timeline Time Display
**Error**: Times showing as "17.29l" instead of "5:29 PM"

**Root Cause**: 
- Timezone mismatch (UTC vs IST)
- Frontend not converting timestamps correctly

**Fix**: 
- Ensure backend stores timezone-aware timestamps
- Frontend converts to user's local timezone for display

---

## 📝 NEXT STEPS

1. **IMMEDIATE** (Do Now):
   - Run Firestore field audit script
   - Document actual field names in database
   - Create migration plan based on findings

2. **SHORT-TERM** (Today):
   - Fix field naming inconsistencies
   - Update models and queries
   - Deploy indexes
   - Test complete flow

3. **LONG-TERM** (Future):
   - Add automated tests for field naming
   - Add linting rules to enforce consistency
   - Document naming conventions in README

---

## ✅ SUCCESS CRITERIA

- [ ] No 500 errors in console
- [ ] Tasks appear in dashboard
- [ ] Meals appear in dashboard
- [ ] Timeline shows activities
- [ ] Times display in correct timezone
- [ ] All queries use correct field names
- [ ] Firestore indexes match actual data
- [ ] Frontend models map correctly

---

## 🔗 RELATED FILES

- `firestore.indexes.json` - Index definitions
- `app/models.py` - Backend models
- `app/services/database.py` - Query logic
- `flutter_app/lib/models/*.dart` - Frontend models
- `flutter_app/lib/providers/dashboard_provider.dart` - Data fetching

---

**Status**: 🔴 CRITICAL - Blocking user from using app
**Priority**: P0 - Fix immediately
**Estimated Time**: 45 minutes (audit + fix + test)
