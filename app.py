"""
LearnHub – Online Education Platform
Main Flask application.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import get_db, init_db, seed_courses


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")


# ---------------------------------------------------------------------------
# Database lifecycle
# ---------------------------------------------------------------------------

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection when the app context ends."""
    db = getattr(app, "_database", None)
    if db is not None:
        db.close()


def setup_database():
    """Ensure the database tables exist and seed sample data."""
    with app.app_context():
        db = get_db()
        init_db(db)
        seed_courses(db)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    """Home page – course catalogue."""
    db = get_db()
    courses = db.execute(
        "SELECT id, title, short_description, instructor, duration, level "
        "FROM courses ORDER BY id"
    ).fetchall()
    return render_template("home.html", courses=courses)


@app.route("/course/<int:course_id>")
def course_detail(course_id):
    """Detail page for a single course."""
    db = get_db()
    course = db.execute(
        "SELECT id, title, short_description, long_description, instructor, "
        "duration, level, prerequisites FROM courses WHERE id = ?",
        (course_id,),
    ).fetchone()
    if course is None:
        flash("Course not found.", "error")
        return redirect(url_for("home"))
    return render_template("course_detail.html", course=course)


@app.route("/enroll/<int:course_id>", methods=["GET", "POST"])
def enroll(course_id):
    """Enrollment form for a course."""
    db = get_db()
    course = db.execute(
        "SELECT id, title FROM courses WHERE id = ?", (course_id,)
    ).fetchone()
    if course is None:
        flash("Course not found.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        # --- validation ---
        errors = []
        if not name:
            errors.append("Full name is required.")
        if not email:
            errors.append("Email address is required.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            errors.append("Please enter a valid email address.")

        # Check for duplicate enrollment
        if not errors:
            existing = db.execute(
                "SELECT id FROM enrollments WHERE email = ? AND course_id = ?",
                (email, course_id),
            ).fetchone()
            if existing:
                errors.append("This email is already enrolled in this course.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("enroll.html", course=course, name=name, email=email)

        db.execute(
            "INSERT INTO enrollments (course_id, student_name, email) VALUES (?, ?, ?)",
            (course_id, name, email),
        )
        db.commit()
        flash(f"Successfully enrolled in {course['title']}!", "success")
        return redirect(url_for("my_enrollments", email=email))

    return render_template("enroll.html", course=course, name="", email="")


@app.route("/my-enrollments")
def my_enrollments():
    """Display enrollments for a given email address."""
    email = request.args.get("email", "").strip()
    enrollments = []

    if email:
        db = get_db()
        enrollments = db.execute(
            "SELECT e.id, e.student_name, e.email, e.enrolled_at, "
            "c.title AS course_title, c.instructor, c.level "
            "FROM enrollments e "
            "JOIN courses c ON e.course_id = c.id "
            "WHERE e.email = ? "
            "ORDER BY e.enrolled_at DESC",
            (email,),
        ).fetchall()

    return render_template("my_enrollments.html", enrollments=enrollments, email=email)


@app.route("/health")
def health():
    """Health-check endpoint for load balancers and CI/CD probes."""
    return jsonify({"status": "healthy"}), 200


# ---------------------------------------------------------------------------
# Initialise database (runs on import so gunicorn also seeds the DB)
# ---------------------------------------------------------------------------
setup_database()

# ---------------------------------------------------------------------------
# Entry point (development server)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
