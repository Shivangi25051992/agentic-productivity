## Admin UI

Static admin interface is served from `app/static/admin/`:
- `admin_login.html`: secure login page
- `admin_dashboard.html`: dashboard with API config, logs, health
- `admin_styles.css`: premium design system
- `admin_scripts.js`: interactivity, auth, toasts, API calls
- `admin_icons.svg`: SVG sprite

### Opening the UI
Serve static files from your web server (or add a FastAPI StaticFiles mount). Example dev usage:

```python
from fastapi.staticfiles import StaticFiles
app.mount("/admin-ui", StaticFiles(directory="app/static/admin"), name="admin-ui")
# Open http://localhost:8000/admin-ui/admin_login.html
```

### Authentication
- Uses admin token API (`/admin/login`, `/admin/logout`, `/admin/verify`).
- Token stored in `sessionStorage` under `admin_token`.

### Security
- CSP/XFO headers added in HTML.
- Basic CSRF placeholder provided; integrate with server-side CSRF for production.






