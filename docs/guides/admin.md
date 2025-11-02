## Admin Configuration Management

### Endpoints
- Create config: POST `/admin/config`
- Active config: GET `/admin/config/active`
- History: GET `/admin/config/history`
- Activate: PUT `/admin/config/{config_id}/activate`
- Update: PUT `/admin/config/{config_id}`
- Delete (soft): DELETE `/admin/config/{config_id}`
- Test: POST `/admin/config/test`

All require admin token. Sensitive fields are masked in responses.







