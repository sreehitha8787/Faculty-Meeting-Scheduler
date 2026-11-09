MAHINDRA UNIVERSITY STAFF CALENDAR — COMPLETE PROJECT PACKAGE

This archive contains the React/Vite frontend, Django REST Framework backend, a fresh SQLite demo database, and 50 fictional sample faculty accounts.

WHAT IS INCLUDED
- React + Vite frontend with the approved light MU branding and username-only login screen.
- Django REST API with JWT authentication and protected staff endpoints.
- 50 fictional faculty users: MU-101 through MU-150.
- Usernames contain letters and digits only (example: ananyarao101).
- 250 weekly timetable rows (5 weekdays per faculty member).
- 50 sample meeting availability records.
- Public holiday register covering the Telangana reference holidays for 2027 through January 2028, with authenticated GET /api/holidays/ endpoint.
- Academic calendar publishing for department heads and administrators.
- WebSocket notification delivery and SMTP-configurable invitation emails.
- Optional browser push notifications through a service worker and VAPID keys.
- Browser push key material is encrypted before it is stored in the application database.
- PostgreSQL-ready configuration through `DATABASE_URL`; SQLite remains the local default.
- Backend availability endpoint rejects configured public holidays with HTTP 409.
- Django admin registration for faculty profiles, timetables, meeting slots and holidays.
- India timezone set to Asia/Kolkata.

DEMO LOGIN
Username: ananyarao101
Password: Demo@12345
All 50 demo users share this temporary password. Change it before any shared deployment.

WINDOWS SETUP
1. Extract this ZIP to a normal writable folder.
2. Open two VS Code terminals.

BACKEND TERMINAL:
  cd Djando_Tutorials\calendar_project
  py -m venv .venv
  .venv\Scripts\Activate.ps1
  python -m pip install -r requirments.txt
  python manage.py check
  python manage.py migrate
  python manage.py runserver

The included db.sqlite3 is already initialized with the 50 demo accounts, timetable rows, meeting availability records and holiday list. Back it up before running any reset command. `python manage.py seed_demo_data` is safe to rerun for the generated demo records. `--reset-demo` deletes and recreates those demo users and their related records.

FRONTEND TERMINAL:
  cd Djando_Tutorials\frontend
  npm install
  npm run dev

Open the Vite URL shown in the terminal (usually http://localhost:5173).

ADMIN ACCESS
Create a separate admin account using:
  python manage.py createsuperuser
Then open http://127.0.0.1:8000/admin/.

IMPORTANT FEATURE / DEPLOYMENT NOTES
- The holiday register is a Telangana reference dataset sourced from public holiday calendars, not an official Mahindra University holiday calendar. Confirm dates and state-specific observances with the university before enabling holiday blocks for real users. Islamic festival dates can change with moon sighting.
- The weekly timetable is recurring by weekday, so the generated schedule applies to 2027 as well as other calendar years.
- The calendar frontend displays saved busy slots, scheduled meetings, and holiday data. Scheduled meetings support faculty invitations, in-workspace notifications, and accept/reject responses.
- Meeting availability is calculated from the current timetable, busy meeting-slot records, and active scheduled meetings. The current UI is not a full room/resource booking system.
- To enable browser push, set the same VAPID public key in the frontend as `VITE_VAPID_PUBLIC_KEY`, and set `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_ADMIN_EMAIL`, and a dedicated random `PUSH_ENCRYPTION_KEY` in the backend environment. Users can then choose “Enable browser alerts” from the notification bell.
- Email invitations require SMTP environment variables, and WebSockets require running the ASGI server.
- Department heads may publish events for their own department; administrators may publish university-wide events.
- Demo records are fictional and must not be represented as actual Mahindra University staff data.
- For production use PostgreSQL with provider-managed disk encryption and encrypted backups, HTTPS, a strong secret key from environment variables, DEBUG=False, correct ALLOWED_HOSTS/CORS origins, secure token lifecycle, backups, and university-approved identity management. Set `DATABASE_SSLMODE=require` (the default when `DATABASE_URL` is used). Django field-level encryption protects stored push keys, but full database-at-rest encryption must be enabled and verified at the PostgreSQL host/provider; local SQLite is not a suitable encrypted production database. Never deploy the shared demo password.
