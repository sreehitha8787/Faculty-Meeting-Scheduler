# MU Staff Calendar Website — Fixes Applied

This update keeps the existing React + Django project structure and addresses the first four priority items.

## Changes made

1. **Login and protected routes**
   - Login stores the returned JWT access token and authenticated username.
   - Protected routes now wrap the home, meeting-slot, and calendar pages.
   - A shared Axios client adds the bearer token to API requests and clears local authentication on an unauthorized response.
   - Home timetable fetch now uses the authenticated API instead of passing a username in the URL.
   - Logout clears the token and username.

2. **Availability search**
   - Search now uses a real date rather than only a weekday name.
   - Backend validates the date and time interval and checks overlap against recurring timetable classes and busy meeting slots on that exact date.
   - API results use consistent `{username, department}` objects and the UI displays them correctly.
   - Invalid or reversed time intervals return a clear 400 response.

3. **Private API access**
   - JWT authentication is enabled in Django REST Framework.
   - Timetable, meeting-slot, and availability endpoints require authentication.
   - A staff member can read or modify only their own timetable/meeting-slot records through the viewsets.
   - Timetable endpoints return the authenticated user's records, regardless of any username query parameter.
   - The all-records diagnostic endpoint is restricted to Django staff/admin users.
   - The insecure GET login endpoint that accepted a password in the URL has been removed.
   - Automatic creation of demo accounts with passwords embedded in source code has been disabled.
   - CORS is restricted to the local Vite development origins by default; hosts and key can be configured through environment variables.

4. **Calendar data**
   - Random `Math.random()` event markers have been removed.
   - The calendar now loads the authenticated user's saved busy meeting slots from the API, marks dates with saved entries, supports month navigation, and lists busy times.
   - The calendar clearly notes that academic events are not yet implemented; this patch does not pretend to add the missing academic-event database model or publishing workflow.

## Files changed

- `frontend/src/api.js` (new)
- `frontend/src/App.jsx`
- `frontend/src/components/ProtectedRoute.jsx`
- `frontend/src/pages/Login.jsx`
- `frontend/src/pages/Home.jsx`
- `frontend/src/pages/MeetingSlots.jsx`
- `frontend/src/pages/Calendar.jsx`
- `calendar_project/calendar_project/settings.py`
- `calendar_project/faculty_calendar/apps.py`
- `calendar_project/faculty_calendar/signals.py`
- `calendar_project/faculty_calendar/serializers.py`
- `calendar_project/faculty_calendar/views.py`
- `calendar_project/faculty_calendar/urls.py`
- `calendar_project/faculty_calendar/tests.py`

## Validation

- Django system check: passed.
- Django app tests: 5 passed.
- Frontend ESLint: passed.
- Vite production build could not be verified in the supplied dependency folder because its Rollup platform-specific optional package is missing. Install dependencies afresh in the frontend folder (`npm install`) before running `npm run build`.

## Important notes

- No database schema change was made, so no new migration is required for these fixes.
- The calendar currently shows busy meeting slots only. Academic-event models, department-head publishing, notifications, and true real-time synchronization remain future implementation work.
- Before deployment, set a strong `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=false`, configure `DJANGO_ALLOWED_HOSTS`, and set `CORS_ALLOWED_ORIGINS` for the actual frontend origin.

## New database package updates (November 2026)
- Included a freshly seeded SQLite database with 50 synthetic faculty users, 250 timetable rows, 50 availability rows, and 20 sample holiday rows.
- Staff usernames are alphanumeric only, for example `ananyarao101`; login accepts staff username only and no longer falls back to email.
- Added `PublicHoliday` model, migration `0004_publicholiday`, admin management, and authenticated `/api/holidays/` endpoint.
- Faculty availability lookup returns HTTP 409 when the requested date is an active public holiday.
- Django timezone is set to Asia/Kolkata.
- The full invite/accept meeting workflow, push/email notifications, WebSocket live synchronization and academic-calendar publishing are not implemented in this package; see `README_FIRST.txt`.
