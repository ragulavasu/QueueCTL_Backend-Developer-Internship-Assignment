import argparse
import json
import os
from datetime import datetime

JOBS_FILE = "jobs.json"

# Basic storage functions (temporary, JSON-based)

def load_jobs():
    if not os.path.exists(JOBS_FILE):
        return []
    with open(JOBS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_jobs(jobs):
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=4)


# CLI command functions

def enqueue_job(job_json):
    try:
        job = json.loads(job_json)
        job["state"] = "pending"
        job["attempts"] = 0
        job["created_at"] = datetime.utcnow().isoformat()
        job["updated_at"] = job["created_at"]
    except json.JSONDecodeError:
        print("Invalid job JSON format.")
        return

    jobs = load_jobs()
    jobs.append(job)
    save_jobs(jobs)
    print(f"Job '{job['id']}' enqueued successfully.")


def list_jobs(state=None):
    jobs = load_jobs()
    if state:
        jobs = [j for j in jobs if j["state"] == state]
    if not jobs:
        print("No jobs found.")
        return
    print(f"Jobs (state: {state or 'all'}):")
    for j in jobs:
        print(f"- {j['id']} | {j['command']} | {j['state']}")


def status_summary():
    jobs = load_jobs()
    summary = {}
    for j in jobs:
        summary[j["state"]] = summary.get(j["state"], 0) + 1
    print("Job Status Summary:")
    for s, c in summary.items():
        print(f"  {s}: {c}")
    if not summary:
        print("  No jobs found.")


# CLI setup

def main():
    parser = argparse.ArgumentParser(
        description="QueueCTL - Simple Background Job Queue System"
    )
    subparsers = parser.add_subparsers(dest="command")

    # enqueue
    enqueue_parser = subparsers.add_parser("enqueue", help="Add a new job to the queue")
    enqueue_parser.add_argument("job_json", help="Job JSON string")

    # list
    list_parser = subparsers.add_parser("list", help="List jobs by state")
    list_parser.add_argument("--state", help="Filter by state", required=False)

    # status
    subparsers.add_parser("status", help="Show summary of all job states")

    args = parser.parse_args()

    if args.command == "enqueue":
        enqueue_job(args.job_json)
    elif args.command == "list":
        list_jobs(args.state)
    elif args.command == "status":
        status_summary()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
