"""
Tests for the LearnHub Flask application.

Run with:  pytest tests/ -v
"""

import os
import tempfile
import pytest
from flask import g
from app import app
from database import get_db, init_db, seed_courses


@pytest.fixture
def client():
    """Create a test client with a fresh temporary database for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    app.config["TESTING"] = True
    os.environ["DATABASE_PATH"] = db_path

    # Re-import database module so it picks up the new path
    import database
    database.DATABASE = db_path

    with app.app_context():
        db = get_db()
        init_db(db)
        seed_courses(db)

    with app.test_client() as client:
        yield client

    # Close any open SQLite connection before deleting the file (Windows needs this)
    with app.app_context():
        db = g.pop("db", None)
        if db is not None:
            db.close()

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        pass  # On Windows the file may still be briefly locked; ignore


# --------------------------------------------------------------------------
# Health check
# --------------------------------------------------------------------------

class TestHealthCheck:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_json(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert data["status"] == "healthy"


# --------------------------------------------------------------------------
# Home page
# --------------------------------------------------------------------------

class TestHomePage:
    def test_home_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_home_contains_course_titles(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        assert "Introduction to Cloud Computing" in html
        assert "DevOps Practices with Jenkins and Docker" in html

    def test_home_contains_nav_links(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        assert "Courses" in html
        assert "My Enrollments" in html


# --------------------------------------------------------------------------
# Course detail page
# --------------------------------------------------------------------------

class TestCourseDetail:
    def test_valid_course_returns_200(self, client):
        resp = client.get("/course/1")
        assert resp.status_code == 200

    def test_valid_course_shows_description(self, client):
        resp = client.get("/course/1")
        html = resp.data.decode()
        assert "Introduction to Cloud Computing" in html
        assert "Dr. Meera Krishnan" in html

    def test_invalid_course_redirects(self, client):
        resp = client.get("/course/9999")
        assert resp.status_code == 302


# --------------------------------------------------------------------------
# Enrollment form (GET)
# --------------------------------------------------------------------------

class TestEnrollFormGet:
    def test_enroll_page_returns_200(self, client):
        resp = client.get("/enroll/1")
        assert resp.status_code == 200

    def test_enroll_page_shows_course_title(self, client):
        resp = client.get("/enroll/1")
        html = resp.data.decode()
        assert "Introduction to Cloud Computing" in html

    def test_enroll_invalid_course_redirects(self, client):
        resp = client.get("/enroll/9999")
        assert resp.status_code == 302


# --------------------------------------------------------------------------
# Enrollment form (POST) – validation
# --------------------------------------------------------------------------

class TestEnrollFormPost:
    def test_successful_enrollment_redirects(self, client):
        resp = client.post("/enroll/1", data={
            "name": "Test Student",
            "email": "student@example.com",
        })
        assert resp.status_code == 302
        assert "/my-enrollments" in resp.headers["Location"]

    def test_missing_name_shows_error(self, client):
        resp = client.post("/enroll/1", data={
            "name": "",
            "email": "student@example.com",
        })
        assert resp.status_code == 200
        assert b"Full name is required" in resp.data

    def test_missing_email_shows_error(self, client):
        resp = client.post("/enroll/1", data={
            "name": "Test Student",
            "email": "",
        })
        assert resp.status_code == 200
        assert b"Email address is required" in resp.data

    def test_invalid_email_shows_error(self, client):
        resp = client.post("/enroll/1", data={
            "name": "Test Student",
            "email": "not-an-email",
        })
        assert resp.status_code == 200
        assert b"valid email" in resp.data

    def test_duplicate_enrollment_shows_error(self, client):
        # First enrollment succeeds
        client.post("/enroll/1", data={
            "name": "Test Student",
            "email": "dup@example.com",
        })
        # Second enrollment for same course + email fails
        resp = client.post("/enroll/1", data={
            "name": "Test Student",
            "email": "dup@example.com",
        })
        assert resp.status_code == 200
        assert b"already enrolled" in resp.data


# --------------------------------------------------------------------------
# My Enrollments page
# --------------------------------------------------------------------------

class TestMyEnrollments:
    def test_page_returns_200(self, client):
        resp = client.get("/my-enrollments")
        assert resp.status_code == 200

    def test_empty_email_shows_lookup_form(self, client):
        resp = client.get("/my-enrollments")
        html = resp.data.decode()
        assert "My Enrollments" in html
        # Should not show "No enrollments found" when no email searched
        assert "No enrollments found" not in html

    def test_unknown_email_shows_empty_state(self, client):
        resp = client.get("/my-enrollments?email=nobody@example.com")
        html = resp.data.decode()
        assert "No enrollments found" in html

    def test_enrolled_course_appears(self, client):
        # Enroll first
        client.post("/enroll/2", data={
            "name": "Akhil H",
            "email": "akhil@test.com",
        })
        resp = client.get("/my-enrollments?email=akhil@test.com")
        html = resp.data.decode()
        assert "DevOps Practices with Jenkins and Docker" in html
        assert "Akhil H" in html
