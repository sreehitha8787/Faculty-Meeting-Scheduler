# MU Staff Calendar — UI Redesign

This update preserves the existing React + Vite frontend and Django REST Framework backend. It changes the frontend presentation and page layout without introducing new backend models or API contracts.

## Design changes

- Replaced the slide-out navigation with a fixed left sidebar on desktop and a responsive drawer on small screens.
- Added consistent Mahindra University red, white, light-grey and charcoal styling.
- Removed dark-mode state, localStorage preference handling, and dark-mode controls from the Home, Calendar and Meeting Slots pages.
- Added a calendar-first dashboard with a selectable mini calendar, schedule summary cards, selected-day timetable, and the existing saved weekly timetable.
- Redesigned Meeting Slots with aligned date/time filters, clearer available/busy faculty results, loading and error states, and responsive cards.
- Redesigned the full calendar with month navigation, selected-day details, saved busy-slot indicators and a monthly list.
- Centralized navigation, user menu and logout behavior in the shared Layout component to avoid duplicate headers and overlapping side panels.
- Retained the existing API calls and JWT API client.

## Existing limitations intentionally not represented as complete

- Academic-event creation and publishing are not implemented in this UI update.
- Meeting creation, invitations and booking confirmation are not implemented.
- Real-time WebSocket synchronization and email reminders are not implemented.
- The calendar currently displays saved busy meeting slots returned by the existing `/meetings/` API.

## Files changed

- `frontend/src/App.jsx`
- `frontend/src/App.css`
- `frontend/src/index.css`
- `frontend/src/components/Layout.jsx`
- `frontend/src/pages/Home.jsx`
- `frontend/src/pages/MeetingSlots.jsx`
- `frontend/src/pages/Calendar.jsx`

## Validation performed in this build environment

- JSX/JavaScript syntax transpilation check passed for every file under `frontend/src` using the installed TypeScript compiler.
- Dark-mode feature references were searched for and removed.
- `npm run lint` and `npm run build` could not run here because the extracted frontend has no complete `node_modules` installation; dependency installation timed out in this environment.
- Django checks could not be rerun in this environment because Django is not installed in the current container Python. Backend files were not modified in this redesign.

## Run locally on Windows

Backend terminal:

```powershell
cd .\Djando_Tutorials\calendar_project
python manage.py runserver
```

Frontend terminal:

```powershell
cd .\Djando_Tutorials\frontend
npm install
npm run dev
```

Open the Vite local URL, usually `http://localhost:5173/`.
