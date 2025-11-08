import json
import os
from datetime import datetime
from threading import Lock

JOBS_FILE = "jobs.json"
DLQ_FILE = "dlq.json"
file_lock = Lock()


def _load_file(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_file(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def add_job(job_data):
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
    with file_lock:
        jobs = _load_file(JOBS_FILE)
        if state:
            jobs = [j for j in jobs if j["state"] == state]
        return jobs


def update_job_state(job_id, new_state):
    with file_lock:
        jobs = _load_file(JOBS_FILE)
        for job in jobs:
            if job["id"] == job_id:
                job["state"] = new_state
                job["updated_at"] = datetime.utcnow().isoformat()
        _save_file(JOBS_FILE, jobs)


def get_status_summary():
    jobs = _load_file(JOBS_FILE)
    summary = {}
    for j in jobs:
        summary[j["state"]] = summary.get(j["state"], 0) + 1
    return summary


def move_to_dlq(job):
    with file_lock:
        dlq = _load_file(DLQ_FILE)
        job["state"] = "dead"
        job["updated_at"] = datetime.utcnow().isoformat()
        dlq.append(job)
        _save_file(DLQ_FILE, dlq)
