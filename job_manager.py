import json
import os
from datetime import datetime
from threading import Lock

JOBS_FILE = "jobs.json"
DLQ_FILE = "dlq.json"

file_lock = Lock()


def _load_file(path):
    """Load JSON data from file. Return [] if missing or invalid."""
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_file(path, data):
    """Write JSON data to file safely."""
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def add_job(job_data):
    """Add a new job to the main queue."""
    with file_lock:
        jobs = _load_file(JOBS_FILE)
        now = datetime.utcnow().isoformat()
        job_data.update({
            "state": "pending",
            "attempts": 0,
            "created_at": now,
            "updated_at": now
        })
        jobs.append(job_data)
        _save_file(JOBS_FILE, jobs)


def get_jobs(state=None):
    """Fetch all jobs, optionally filtered by state."""
    with file_lock:
        jobs = _load_file(JOBS_FILE)
        if state:
            jobs = [j for j in jobs if j["state"] == state]
        return jobs


def update_job_state(job_id, new_state):
    """Change the state of a specific job."""
    with file_lock:
        jobs = _load_file(JOBS_FILE)
        for job in jobs:
            if job["id"] == job_id:
                job["state"] = new_state
                job["updated_at"] = datetime.utcnow().isoformat()
        _save_file(JOBS_FILE, jobs)


def update_job_attempts(job_id, attempts):
    """Update the attempt count of a specific job."""
    with file_lock:
        jobs = _load_file(JOBS_FILE)
        for job in jobs:
            if job["id"] == job_id:
                job["attempts"] = attempts
                job["updated_at"] = datetime.utcnow().isoformat()
        _save_file(JOBS_FILE, jobs)


def get_status_summary():
    """Return a summary of job counts by state."""
    jobs = _load_file(JOBS_FILE)
    summary = {}
    for j in jobs:
        summary[j["state"]] = summary.get(j["state"], 0) + 1
    return summary



def move_to_dlq(job):
    """Move a failed job from jobs.json to dlq.json."""
    with file_lock:
        jobs = _load_file(JOBS_FILE)
        job_to_move = None

        for j in jobs:
            if j["id"] == job["id"]:
                job_to_move = j.copy()
                break

        if not job_to_move:
            return  

        jobs = [j for j in jobs if j["id"] != job["id"]]
        _save_file(JOBS_FILE, jobs)

        dlq = _load_file(DLQ_FILE)
        job_to_move["state"] = "dead"
        job_to_move["updated_at"] = datetime.utcnow().isoformat()
        dlq.append(job_to_move)
        _save_file(DLQ_FILE, dlq)


def get_dlq_jobs():
    """Return all jobs currently in the DLQ."""
    with file_lock:
        return _load_file(DLQ_FILE)


def retry_dlq_job(job_id):
    """Move a DLQ job back to the main queue (reset for retry)."""
    with file_lock:
        dlq = _load_file(DLQ_FILE)
        job = None

        for j in dlq:
            if j["id"] == job_id:
                job = j
                break

        if not job:
            return False  

        dlq = [j for j in dlq if j["id"] != job_id]
        _save_file(DLQ_FILE, dlq)

        jobs = _load_file(JOBS_FILE)
        job["state"] = "pending"
        job["attempts"] = 0
        job["updated_at"] = datetime.utcnow().isoformat()
        jobs.append(job)
        _save_file(JOBS_FILE, jobs)

        return True
