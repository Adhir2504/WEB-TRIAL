# UniBook Progress (Beginner Summary)

This repo contains a Django booking website. Below is a simple list of what has already been finished (based on the original plan) and what is still left to do.

---

## ✅ What Has Been Implemented

### 1. HTML layouts & CSS
- All Figma screens were converted to Django templates: home, facilities, facility details, calendar, profile, login/register, and admin forms.
- Global styling lives in `static/css/mystyle.css`; pages can add small inline tweaks.
- Facilities page now uses dynamic cards with badges, availability info, and filters.
- Calendar page shows a visual month grid plus clickable day pills that pull data from the database.

### 2. Django models & views
- Models cover users, facilities, courts, slots, bookings, availability, blackout periods, notifications, and audit logs.
- Views were built for: authentication (login/logout/register), profile, facility list/detail/booking, calendar, search, booking create/cancel, and admin creation pages for facilities/courts/slots/availability/blackouts.
- URLs connect all pages, and `login_required` plus role checks guard admin actions.

### 3. Forms (GET & POST)
- ModelForms exist for every model plus custom registration/profile forms.
- Regex validation added for usernames, emails, phone numbers, student IDs, department names, facility titles, etc.
- Forms return clear error messages and success notifications (Django messages framework).

### 4. Admin site & authentication
- Custom user model with email login.
- Ready-made superuser and student accounts via `python manage.py seed_demo`.
- Navigation adapts based on login state; admin-only links appear only for staff/admin accounts.

### 5. Data & sample content
- `python manage.py seed_demo` fills the database with:
  - Admin: `admin@unibook.mu / Admin123!`
  - Student: `tony@student.mu / Student123!`
  - Five demo facilities with courts, availability blocks, slots, and example bookings.

---

## 🧩 What Still Needs to Be Done

| Area | Next steps |
|------|------------|
| **Images & media** | Replace gradient placeholders with real photos, store uploads in `MEDIA_ROOT`. |
| **Automated tests** | Add unit tests for forms, views, slot rules, and permissions. |
| **Booking safety** | Add DB constraints/locking so two people cannot book the same slot simultaneously. |
| **Calendar polish** | Hook the month grid to real dates and allow navigating months. |
| **User experience** | Add better toasts/spinners, finish student/staff extra info during sign-up, improve accessibility. |
| **Notifications** | Connect email/SMS for booking reminders and cancellations. |
| **Deployment** | Move secrets to `.env`, set `DEBUG=False`, configure production static/media hosting, document deployment. |
| **Analytics & audit** | Display audit logs/usage stats to admins. |
| **Optional API** | Add REST endpoints (Django REST Framework) for mobile/SPA clients. |

---

## ▶️ How to Run Locally

```bash
python -m venv venv
venv\Scripts\activate          # PowerShell on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Visit:
- `http://127.0.0.1:8000/` for the site
- `http://127.0.0.1:8000/admin/` for Django admin (use the seeded admin credentials)

---

Feel free to extend this log as you add features or finish the remaining tasks. Happy building! 🎉

