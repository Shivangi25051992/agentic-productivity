## Authentication

### User auth (Firebase)
- Sign up: POST `/auth/signup` with `{ id_token }`
- Login: POST `/auth/login` with `{ id_token }`
- Current user: GET `/auth/me` with `Authorization: Bearer <id_token>`

### Admin auth (separate)
- Login: POST `/admin/login` with `{ username, password }` → `{ token }`
- Verify: GET `/admin/verify` with `Authorization: Bearer <token>`
- Logout: POST `/admin/logout` with `Authorization: Bearer <token>`

Set env: `ADMIN_USERNAME`, `ADMIN_PASSWORD` (or `ADMIN_PASSWORD_BCRYPT`), `ADMIN_SECRET_KEY`.






