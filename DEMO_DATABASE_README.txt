50 fictional demo faculty accounts are preloaded into calendar_project/db.sqlite3.
Staff IDs: MU-101 through MU-150.
Username pattern: firstnamelastname### using ASCII letters and digits only (example: ananyarao101).
Shared local-only demo password: Demo@12345.

Database counts in the supplied SQLite file:
- 50 auth users
- 50 faculty profiles
- 250 weekly timetable rows
- 50 meeting availability rows
- Reference public-holiday rows covering Telangana calendar data through January 2028

Run from calendar_project:
  python manage.py migrate
  python manage.py seed_demo_data

The seed command is idempotent for the generated usernames. `--reset-demo` recreates generated demo users and related schedule rows. Back up db.sqlite3 first.
All staff data is synthetic, not actual Mahindra University data. The holiday list is a starter reference and must be checked against the official MU calendar.
