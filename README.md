# LearnHub – Online Education Platform

A minimal online education portal built with **Python Flask**, **Jinja2 templates**, **plain CSS**, and **SQLite**. Created as a Cloud Computing course project — the primary goal is a working web application that is easy to Dockerise and deploy via a Jenkins CI/CD pipeline to AWS EC2.

---

## Features

| Page | Route | Description |
|---|---|---|
| Home | `/` | Course catalogue with 6 sample courses |
| Course Detail | `/course/<id>` | Full description, instructor, duration, level, prerequisites |
| Enroll | `/enroll/<id>` | Form to enroll in a course (with validation) |
| My Enrollments | `/my-enrollments` | Look up enrollments by email |
| Health Check | `/health` | Returns `{"status": "healthy"}` — for load balancers and CI probes |

---

## Folder Structure

```
CC Course Project/
├── app.py               # Flask application (routes, config)
├── database.py          # SQLite helpers (schema, seed data)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image definition
├── .gitignore           # Files excluded from Git
├── README.md            # This file
├── templates/           # Jinja2 HTML templates
│   ├── base.html        #   Shared layout (nav, footer, flash messages)
│   ├── home.html        #   Course catalogue
│   ├── course_detail.html  # Single course view
│   ├── enroll.html      #   Enrollment form
│   └── my_enrollments.html # Enrollment lookup
└── static/
    └── style.css        # Stylesheet
```

---

## Running Locally

### Prerequisites

- Python 3.10 or newer

### Steps

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
#    Windows (PowerShell):
.\venv\Scripts\Activate.ps1
#    macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

The app starts on **http://localhost:5000**. The SQLite database (`learnhub.db`) is created automatically on first run with sample courses pre-loaded.

### Environment Variables (optional)

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `dev-secret-change-in-production` | Flask session secret |
| `DATABASE_PATH` | `learnhub.db` | Path to the SQLite file |
| `PORT` | `5000` | Port the server listens on |
| `FLASK_DEBUG` | `0` | Set to `1` for auto-reload during development |

---

## Running with Docker

```bash
# Build the image
docker build -t learnhub .

# Run the container
docker run -p 5000:5000 learnhub
```

Then open **http://localhost:5000**.

---

## What's Not Included (By Design)

- **User authentication / login** – not needed for the MVP
- **Payment processing** – out of scope
- **Video streaming** – out of scope
- **Jenkins pipeline / AWS deployment** – will be added separately as the CI/CD component of the course project

---

## License

This project is for educational purposes as part of a Cloud Computing course.
