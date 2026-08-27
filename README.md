# Pet Pulse 🐾

A centralized web app for managing pet healthcare — profiles, medical reports,
appointments, insurance, and emergency vet contacts, all in one dashboard.

Built with **Flask**, **Jinja2**, and **SQLite**. Originally a B.Tech (Honors)
project report; rebuilt here as a runnable, minimal reference implementation.

## Features

- **Pet profiles** — name, breed, age, allergies, owner, and photo
- **Medical reports** — upload and reopen reports linked to each pet
- **Appointments** — schedule in-person or virtual vet visits
- **Insurance** — browse plans and link a policy to a pet
- **Emergency contacts** — quick list of nearby vets + a "find vets near me" link

## Tech stack

- Python 3 + [Flask](https://flask.palletsprojects.com/)
- SQLite (via the standard-library `sqlite3` module — no separate DB server needed)
- Jinja2 templates, vanilla CSS/JS (no build step required)

## Getting started

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/pet-pulse.git
cd pet-pulse

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

The SQLite database (`petpulse.db`) and its tables are created automatically
the first time the app runs, along with a few starter insurance plans and
emergency contacts.

## Project structure

```
pet-pulse/
├── app.py                  # App factory / entry point
├── config.py                # Configuration (paths, upload limits)
├── models.py                 # Database schema + query helpers
├── routes.py                  # Flask routes (blueprint)
├── requirements.txt
├── static/
│   ├── css/style.css          # Design system + styles
│   ├── js/main.js              # Mobile nav toggle
│   └── uploads/
│       ├── pets/                 # Uploaded pet photos
│       └── reports/               # Uploaded medical reports
└── templates/
    ├── base.html
    ├── index.html               # Dashboard
    ├── add_pet.html
    ├── update_pet.html
    ├── upload_report.html
    ├── schedule_appointment.html
    ├── emergency_contacts.html
    └── insurance.html
```

## Notes

- This is a teaching/portfolio build: file uploads are stored on local disk,
  and there's no authentication layer — don't use it as-is in production.
- Emergency contacts and insurance plans are seeded once when the database is
  first created; edit `models.py`'s `init_db()` to change the starter data.

## License

MIT — do whatever you'd like with it.
