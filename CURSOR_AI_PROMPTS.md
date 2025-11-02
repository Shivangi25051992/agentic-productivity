# 🤖 CURSOR AI PROMPT SEQUENCE
## Step-by-Step Prompts for Implementation

**Purpose**: Execute the migration and implementation plan using AI assistance  
**Order**: Sequential - complete each prompt before moving to the next

---

## 📋 PROMPT 1: Audit Current State

```
Task: Fetch and document the current Firestore state

Instructions:
1. Read CURRENT_FIRESTORE_STATE.json
2. Verify it matches the live database by checking:
   - All collection names
   - All field names and types
   - All deployed indexes
   - All security rules
3. Create a summary table with:
   - Collection name
   - Document count (estimate)
   - Key fields
   - Indexes (deployed/missing)
   - Security status
4. Highlight any discrepancies between JSON and live state

Output format: Markdown table
```

**Expected Output**: Table showing current state with any gaps highlighted

---

## 📋 PROMPT 2: Compare Current vs Proposed

```
Task: Diff CURRENT_FIRESTORE_STATE.json with PROPOSED_FIRESTORE_MODEL.json

Instructions:
1. Load both JSON files
2. Create a detailed comparison covering:
   - Architecture differences (flat vs subcollections)
   - Security rule changes
   - Index requirements (new, modified, removed)
   - Denormalization strategy
   - Validation rules added
3. For each difference, explain:
   - Why it's needed
   - Impact on performance
   - Impact on security
   - Impact on scalability
4. Identify any potential breaking changes
5. List all scaling/privacy blockers in current model

Output format: Comparison table + narrative explanation
```

**Expected Output**: Detailed diff with rationale for each change

---

## 📋 PROMPT 3: Generate Migration Scripts

```
Task: Create Python migration scripts based on MIGRATION_PLAN.md

Instructions:
1. Create migration_scripts/ directory
2. Write the following scripts:
   
   a) migrate_users.py
      - Migrate user profile data to users/{userId}/profile/current
      - Handle missing fields gracefully
      - Validate data before writing
   
   b) migrate_fitness_logs.py
      - Move fitness_logs to users/{userId}/fitness_logs/{logId}
      - Transform ai_parsed_data to structured format
      - Add date field for querying
      - Group multi-item meals correctly
   
   c) migrate_tasks.py
      - Move tasks to users/{userId}/tasks/{taskId}
      - Remove user_id field (redundant in subcollection)
      - Validate enum fields
   
   d) migrate_chat_history.py
      - Group messages by date into sessions
      - Create users/{userId}/chat_sessions/{sessionId}/messages/{messageId}
      - Set expiresAt for 7-day retention
   
   e) generate_daily_stats.py
      - Calculate daily stats from fitness logs
      - Create users/{userId}/daily_stats/{date}
      - Include calories, macros, counts, streak
   
   f) migrate_all.py
      - Orchestrate all migrations
      - Support --users, --percentage, --env flags
      - Include progress bar and error handling
      - Log all errors for retry

3. Add validation function to verify migration success
4. Add rollback function to undo migration if needed

Output: Complete Python scripts with error handling and logging
```

**Expected Output**: 6 Python files ready to execute

---

## 📋 PROMPT 4: Write Security & Validation Rules

```
Task: Create comprehensive Firestore security and validation rules

Instructions:
1. Update firestore.rules with:
   
   a) User isolation rules
      - Users can only access their own subcollections
      - Check auth.uid === userId for all paths
   
   b) Field validation
      - Validate email format
      - Validate calorie ranges (0-10000)
      - Validate macro ranges (protein 0-500g, carbs 0-1000g, fat 0-500g)
      - Validate enum fields (fitnessGoal, logType, status, priority)
      - Validate dailyCalorieGoal (1200-5000)
   
   c) Type enforcement
      - Ensure all numeric fields are numbers
      - Ensure all string fields are strings
      - Ensure all timestamp fields are timestamps
   
   d) Immutability rules
      - Chat messages cannot be updated (only created/deleted)
      - createdAt timestamp cannot be changed
      - Achievements are read-only for users
   
   e) Rate limiting (if possible)
      - Limit food database queries per user
   
2. Create test cases for security rules:
   - Test user can read own data
   - Test user cannot read other user's data
   - Test invalid data is rejected
   - Test enum validation works
   - Test range validation works

3. Document all rules with comments explaining purpose

Output: Complete firestore.rules file + test cases
```

**Expected Output**: Production-ready security rules with tests

---

## 📋 PROMPT 5: Create Cloud Functions

```
Task: Write Cloud Functions for data retention, cleanup, and denormalization

Instructions:
1. Create cloud_functions/ directory with:
   
   a) cleanupExpiredChats.js
      - Scheduled function (daily at 2am)
      - Query chat_sessions where expiresAt < now
      - Delete session and all messages
      - Log deletion count
   
   b) updateDailyStats.js
      - Firestore trigger on fitness_logs onCreate/onUpdate
      - Calculate daily totals for that date
      - Update users/{userId}/daily_stats/{date}
      - Include: calories, macros, meal/workout counts
   
   c) calculateStreak.js
      - Scheduled function (daily at midnight)
      - Check if user logged anything today
      - Update streak in daily_stats
      - Trigger achievement if milestone reached
   
   d) archiveOldData.js
      - Scheduled function (monthly)
      - Archive fitness_logs and tasks older than 1 year
      - Move to archive collection or Cloud Storage
      - Delete from main collection
   
   e) checkAchievements.js
      - Firestore trigger on daily_stats onUpdate
      - Check for achievement milestones
      - Create achievement document if unlocked
      - Send notification to user

2. Add error handling and retry logic
3. Add Cloud Monitoring integration
4. Add unit tests for each function

Output: Complete Cloud Functions with tests and deployment config
```

**Expected Output**: 5 Cloud Functions ready to deploy

---

## 📋 PROMPT 6: Update Backend Code

```
Task: Update all backend services to use new subcollection structure

Instructions:
1. Update app/services/database.py:
   - Change all queries to use subcollections
   - Remove user_id filters (implicit in path)
   - Use collection groups for cross-user admin queries
   - Add validation before writes
   
2. Update app/main.py:
   - Update chat endpoint to use chat_sessions
   - Update fitness logging to use subcollections
   - Add daily_stats update logic
   - Remove duplicate meal creation logic
   
3. Update app/routers/fitness.py:
   - Update all endpoints to use subcollections
   - Add date-based queries
   - Add log_type filtering
   
4. Update app/routers/profile.py:
   - Update to use profile subcollection
   - Add validation for all fields
   
5. Update app/services/chat_history_service.py:
   - Update to use chat_sessions structure
   - Group messages by session
   - Handle session expiration

6. Add backward compatibility layer:
   - Support both old and new structures during migration
   - Use feature flag to switch between them

7. Add integration tests for all endpoints

Output: Updated backend code with tests
```

**Expected Output**: Backend code working with new structure

---

## 📋 PROMPT 7: Update Frontend Code

```
Task: Update Flutter app to work with new backend structure

Instructions:
1. Update flutter_app/lib/services/api_service.dart:
   - No changes needed (backend handles subcollections internally)
   - Add error handling for new error types
   
2. Update flutter_app/lib/providers/:
   - Update data models to match new structure
   - Add daily_stats provider
   - Update fitness_provider for new log structure
   - Update chat_provider for sessions
   
3. Update flutter_app/lib/screens/:
   - Update home screen to use daily_stats
   - Update timeline to handle new log structure
   - Update chat screen for sessions
   
4. Add loading states and error handling
5. Add offline support (cache daily_stats)
6. Add pull-to-refresh on all screens

7. Test all user flows:
   - Onboarding
   - Logging meals/workouts
   - Chat assistant
   - Viewing timeline
   - Viewing stats

Output: Updated Flutter app with tests
```

**Expected Output**: Frontend working end-to-end

---

## 📋 PROMPT 8: Monitoring & Compliance

```
Task: Set up monitoring, alerting, and compliance tools

Instructions:
1. Configure Cloud Monitoring:
   - Dashboard for key metrics:
     * Firestore read/write operations
     * Query latency (p50, p95, p99)
     * Error rates by endpoint
     * Active users
     * Daily active users (DAU)
     * Cost per user
   
   - Alerts for:
     * Error rate > 1%
     * Query latency p95 > 500ms
     * Daily cost > $100
     * Security rule violations
     * Failed Cloud Functions

2. Set up Error Tracking:
   - Integrate Sentry or Cloud Error Reporting
   - Track all backend errors
   - Track all frontend errors
   - Group by error type and user

3. Set up Cost Monitoring:
   - Budget alerts at 50%, 75%, 90%
   - Cost breakdown by collection
   - Cost per user calculation
   - Optimization recommendations

4. GDPR/CCPA Compliance:
   - User data export API:
     * Export all user data as JSON
     * Include all subcollections
     * Provide download link
   
   - User data deletion API:
     * Delete users/{userId} document
     * All subcollections deleted automatically
     * Log deletion in audit log
   
   - Audit logging:
     * Log all data access
     * Log all data modifications
     * Log all deletions
     * Retain logs for 2 years

5. Privacy Policy updates:
   - Document data retention (7 days for chat, 1 year for logs)
   - Document data sharing (none)
   - Document user rights (export, delete)

Output: Monitoring dashboards, alert configs, compliance APIs
```

**Expected Output**: Full monitoring and compliance setup

---

## 📋 PROMPT 9: Performance Testing

```
Task: Run comprehensive performance tests and optimize

Instructions:
1. Load Testing:
   - Simulate 100 concurrent users
   - Test all critical paths:
     * User login
     * Dashboard load
     * Meal logging
     * Chat interaction
     * Timeline view
   - Measure:
     * Response times (p50, p95, p99)
     * Error rates
     * Throughput (requests/second)

2. Query Optimization:
   - Identify slow queries (>200ms)
   - Check if indexes are being used
   - Optimize query patterns
   - Add caching where appropriate

3. Cost Optimization:
   - Identify expensive queries
   - Reduce unnecessary reads
   - Use denormalized data where possible
   - Implement query result caching

4. Scalability Testing:
   - Test with 1K, 10K, 100K users
   - Identify bottlenecks
   - Plan for horizontal scaling

5. Generate performance report:
   - Before vs after comparison
   - Cost analysis
   - Scalability projections
   - Optimization recommendations

Output: Performance test results and optimization plan
```

**Expected Output**: Performance report with recommendations

---

## 📋 PROMPT 10: Documentation & Handoff

```
Task: Create comprehensive documentation for the new architecture

Instructions:
1. Architecture Documentation:
   - Data model diagram
   - Collection structure
   - Relationships between collections
   - Query patterns
   - Security model

2. API Documentation:
   - All endpoints with examples
   - Request/response formats
   - Error codes and handling
   - Rate limits
   - Authentication

3. Developer Guide:
   - How to add new features
   - How to query data
   - How to add new collections
   - How to update security rules
   - How to deploy changes

4. Operations Guide:
   - How to monitor the system
   - How to handle incidents
   - How to scale the system
   - How to backup/restore data
   - How to handle user requests (export, delete)

5. Migration Documentation:
   - What was changed and why
   - Migration process
   - Rollback procedure
   - Known issues and workarounds
   - Future improvements

Output: Complete documentation set
```

**Expected Output**: Production-ready documentation

---

## 🎯 EXECUTION ORDER

1. ✅ **Prompt 1** → Verify current state
2. ✅ **Prompt 2** → Understand changes needed
3. ⏳ **Prompt 3** → Create migration scripts
4. ⏳ **Prompt 4** → Secure the database
5. ⏳ **Prompt 5** → Automate maintenance
6. ⏳ **Prompt 6** → Update backend
7. ⏳ **Prompt 7** → Update frontend
8. ⏳ **Prompt 8** → Add monitoring
9. ⏳ **Prompt 9** → Optimize performance
10. ⏳ **Prompt 10** → Document everything

---

## 📊 PROGRESS TRACKING

| Prompt | Status | Owner | Duration | Completion Date |
|--------|--------|-------|----------|-----------------|
| 1. Audit | ✅ Done | AI | 1 hour | Nov 2, 2025 |
| 2. Compare | ✅ Done | AI | 1 hour | Nov 2, 2025 |
| 3. Scripts | ⏳ Pending | Backend Dev | 2 days | - |
| 4. Security | ⏳ Pending | Backend Dev | 1 day | - |
| 5. Functions | ⏳ Pending | Backend Dev | 2 days | - |
| 6. Backend | ⏳ Pending | Backend Dev | 2 days | - |
| 7. Frontend | ⏳ Pending | Frontend Dev | 2 days | - |
| 8. Monitoring | ⏳ Pending | DevOps | 1 day | - |
| 9. Testing | ⏳ Pending | QA | 2 days | - |
| 10. Docs | ⏳ Pending | Tech Writer | 1 day | - |

---

**Total Estimated Time**: 14 days (2-3 weeks with testing and validation)

**Next Action**: Start with Prompt 3 to create migration scripts

