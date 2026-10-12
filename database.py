"""
Database helpers – SQLite setup, schema, and seed data.
"""

import os
import sqlite3
from flask import g, current_app

DATABASE = os.environ.get("DATABASE_PATH", "learnhub.db")


def get_db():
    """Return a database connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(db):
    """Create tables if they do not exist."""
    db.executescript("""
        CREATE TABLE IF NOT EXISTS courses (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT NOT NULL,
            short_description TEXT NOT NULL,
            long_description TEXT NOT NULL,
            instructor      TEXT NOT NULL,
            duration        TEXT NOT NULL,
            level           TEXT NOT NULL,
            prerequisites   TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id       INTEGER NOT NULL,
            student_name    TEXT NOT NULL,
            email           TEXT NOT NULL,
            enrolled_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """)
    db.commit()


def seed_courses(db):
    """Insert sample courses if the table is empty."""
    count = db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    if count > 0:
        return

    sample_courses = [
        {
            "title": "Introduction to Cloud Computing",
            "short_description": "Understand the fundamentals of cloud infrastructure, service models (IaaS, PaaS, SaaS), and major providers.",
            "long_description": (
                "This course covers the core concepts behind cloud computing, including "
                "virtualisation, multi-tenancy, and the shared responsibility model. You will "
                "explore the differences between public, private, and hybrid clouds, compare AWS, "
                "Azure, and GCP at a high level, and complete hands-on labs that provision virtual "
                "machines and storage buckets. By the end of the course you should be comfortable "
                "reading cloud architecture diagrams and selecting appropriate service tiers for "
                "small-to-medium workloads."
            ),
            "instructor": "Dr. Meera Krishnan",
            "duration": "6 weeks",
            "level": "Beginner",
            "prerequisites": "Basic understanding of operating systems",
        },
        {
            "title": "DevOps Practices with Jenkins and Docker",
            "short_description": "Learn to build CI/CD pipelines using Jenkins, Docker containers, and automated testing.",
            "long_description": (
                "Starting from version-control basics, this course walks through the full "
                "continuous-integration and continuous-delivery lifecycle. Topics include writing "
                "Jenkinsfiles, building and pushing Docker images, running automated test suites "
                "inside containers, and deploying to staging environments. You will set up a "
                "multi-stage pipeline for a sample web application and learn strategies for "
                "rollback, blue-green deployments, and secret management."
            ),
            "instructor": "Prof. Alan Torres",
            "duration": "8 weeks",
            "level": "Intermediate",
            "prerequisites": "Familiarity with Linux command line and Git",
        },
        {
            "title": "AWS Solutions Architect Preparation",
            "short_description": "A structured review of AWS services, architecture best practices, and exam-style problem solving.",
            "long_description": (
                "Designed for students preparing for the AWS Solutions Architect – Associate "
                "certification, this course reviews compute (EC2, Lambda), storage (S3, EBS), "
                "networking (VPC, Route 53), databases (RDS, DynamoDB), and security (IAM, KMS). "
                "Each module includes scenario-based questions that mirror the exam format. "
                "You will also design a small three-tier web application architecture as your "
                "capstone project."
            ),
            "instructor": "Dr. Meera Krishnan",
            "duration": "10 weeks",
            "level": "Intermediate",
            "prerequisites": "Introduction to Cloud Computing or equivalent experience",
        },
        {
            "title": "Linux System Administration Essentials",
            "short_description": "Gain practical skills in managing Linux servers, user accounts, services, and shell scripting.",
            "long_description": (
                "This hands-on course is built around Ubuntu and CentOS environments. You will "
                "learn to navigate the filesystem, manage packages with apt and yum, configure "
                "SSH and firewalls, write Bash scripts for repetitive tasks, and monitor system "
                "resources. The final project asks you to provision and harden a virtual server "
                "ready for hosting a web application."
            ),
            "instructor": "Ms. Fatima Al-Rashid",
            "duration": "5 weeks",
            "level": "Beginner",
            "prerequisites": "None",
        },
        {
            "title": "Containerisation and Kubernetes",
            "short_description": "Move from single-container Docker workflows to orchestrating multi-container applications with Kubernetes.",
            "long_description": (
                "After a quick Docker refresher, this course focuses on Kubernetes concepts: "
                "pods, deployments, services, config maps, and persistent volumes. You will "
                "deploy a microservices application to a local Minikube cluster, set up "
                "horizontal pod autoscaling, and implement rolling updates. The course also "
                "introduces Helm charts and basic observability with Prometheus and Grafana."
            ),
            "instructor": "Prof. Alan Torres",
            "duration": "8 weeks",
            "level": "Advanced",
            "prerequisites": "DevOps Practices with Jenkins and Docker, or equivalent",
        },
        {
            "title": "Database Design and SQL Fundamentals",
            "short_description": "Learn relational database concepts, write SQL queries, and design normalised schemas.",
            "long_description": (
                "Starting from entity-relationship modelling, this course teaches you to design "
                "normalised database schemas and write SQL for creating tables, inserting data, "
                "and querying with joins, subqueries, and aggregations. You will work with SQLite "
                "and PostgreSQL, learn about indexing and query performance, and complete a "
                "project that models and queries a realistic dataset such as a library catalogue "
                "or student records system."
            ),
            "instructor": "Dr. Ravi Patel",
            "duration": "6 weeks",
            "level": "Beginner",
            "prerequisites": "None",
        },
    ]

    for c in sample_courses:
        db.execute(
            "INSERT INTO courses (title, short_description, long_description, "
            "instructor, duration, level, prerequisites) "
            "VALUES (:title, :short_description, :long_description, "
            ":instructor, :duration, :level, :prerequisites)",
            c,
        )
    db.commit()
