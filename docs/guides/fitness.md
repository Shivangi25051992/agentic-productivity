## Fitness Guide

### Log natural language entries
POST `/fitness/log` with `{ text }` (requires user token) → creates `FitnessLog`.

### List logs with filters
GET `/fitness/logs?start=&end=&log_type=&limit=`

### Stats
GET `/fitness/stats?start=&end=` → returns daily/weekly calories and workout counts.







