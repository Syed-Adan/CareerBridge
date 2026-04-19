"""
storage.py — All read/write operations for CareerBridge.

Files created automatically inside the /data folder:
  users.json        — registered accounts
  applications.json — student applications and their statuses
  listings.json     — provider-posted listings
  profiles.json     — student profile info (name, skills, resume filename)
  resumes/          — uploaded PDF files

In production, swap these JSON functions for a real database
(SQLite or PostgreSQL). All function signatures stay the same.
"""

import json
import os
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_DIR    = "data"
RESUME_DIR  = os.path.join(DATA_DIR, "resumes")

USERS_FILE        = os.path.join(DATA_DIR, "users.json")
APPLICATIONS_FILE = os.path.join(DATA_DIR, "applications.json")
LISTINGS_FILE     = os.path.join(DATA_DIR, "listings.json")
PROFILES_FILE     = os.path.join(DATA_DIR, "profiles.json")

VALID_STATUSES = ["applied", "selected", "rejected", "enrolled"]


# ── Helpers ────────────────────────────────────────────────────────────────────
def _ensure_dirs():
    os.makedirs(DATA_DIR,   exist_ok=True)
    os.makedirs(RESUME_DIR, exist_ok=True)


def _read(path, default):
    _ensure_dirs()
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def _write(path, data):
    _ensure_dirs()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ── Users ──────────────────────────────────────────────────────────────────────
def get_user(username: str):
    """Return user dict or None."""
    return _read(USERS_FILE, {}).get(username)


def save_user(username: str, password: str, role: str):
    """
    Create a new user account.
    role must be 'student' or 'provider'.
    NOTE: Passwords stored as plaintext here (prototype only).
    Production should use bcrypt hashing.
    """
    users = _read(USERS_FILE, {})
    users[username] = {"password": password, "role": role}
    _write(USERS_FILE, users)


# ── Profiles ───────────────────────────────────────────────────────────────────
def get_profile(username: str) -> dict:
    """Always returns a dict (empty defaults if no profile yet)."""
    default = {"name": "", "skills": "", "resume_filename": ""}
    return _read(PROFILES_FILE, {}).get(username, default)


def save_profile(username: str, name: str, skills: str, resume_filename: str = ""):
    profiles = _read(PROFILES_FILE, {})
    existing_resume = profiles.get(username, {}).get("resume_filename", "")
    profiles[username] = {
        "name": name,
        "skills": skills,
        # Keep old resume if nothing new was uploaded
        "resume_filename": resume_filename or existing_resume,
    }
    _write(PROFILES_FILE, profiles)


def save_resume(username: str, original_filename: str, file_bytes: bytes) -> str:
    """Write PDF bytes to disk. Returns the stored filename."""
    _ensure_dirs()
    stored_name = f"{username}_{original_filename}"
    with open(os.path.join(RESUME_DIR, stored_name), "wb") as f:
        f.write(file_bytes)
    return stored_name


def get_resume_path(stored_filename: str):
    """Returns full path if the file exists, else None."""
    if not stored_filename:
        return None
    path = os.path.join(RESUME_DIR, stored_filename)
    return path if os.path.exists(path) else None


# ── Applications ───────────────────────────────────────────────────────────────
def load_applications() -> list:
    return _read(APPLICATIONS_FILE, [])


def already_applied(student: str, listing_id: str) -> bool:
    return any(
        a["student"] == student and a["listing_id"] == listing_id
        for a in load_applications()
    )


def apply(student: str, listing_id: str, listing_title: str):
    """
    Save a new application with status='applied'.
    Silently does nothing if the student already applied (duplicate guard).
    """
    if already_applied(student, listing_id):
        return
    apps = load_applications()
    apps.append({
        "student":       student,
        "listing_id":    listing_id,
        "listing_title": listing_title,
        "status":        "applied",
        "applied_on":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    _write(APPLICATIONS_FILE, apps)


def update_status(student: str, listing_id: str, new_status: str):
    """
    Provider updates an applicant's status.
    Ignores unknown status strings (edge-case guard).
    """
    if new_status not in VALID_STATUSES:
        return
    apps = load_applications()
    for a in apps:
        if a["student"] == student and a["listing_id"] == listing_id:
            a["status"] = new_status
            break
    _write(APPLICATIONS_FILE, apps)


# ── Listings (provider-posted) ─────────────────────────────────────────────────
def load_provider_listings() -> list:
    return _read(LISTINGS_FILE, [])


def save_listing(listing: dict):
    listings = load_provider_listings()
    listings.append(listing)
    _write(LISTINGS_FILE, listings)