## Tasks Guide

### Natural language creation
POST `/tasks/create` with `{ text }` (requires user token) → creates parsed task.

### Listing with filters
GET `/tasks?status=&priority=&start_due=&end_due=&limit=`

### Update / Delete
- PATCH `/tasks/{task_id}`
- DELETE `/tasks/{task_id}`






