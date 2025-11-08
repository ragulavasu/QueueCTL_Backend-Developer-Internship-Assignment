import argparse
import json
import job_manager


def enqueue_job(job_json):
    try:
        job_data = json.loads(job_json)
    except json.JSONDecodeError:
        print("Invalid job JSON format.")
        return

    job_manager.add_job(job_data)
    print(f"Job '{job_data['id']}' enqueued successfully.")


def list_jobs(state=None):
    jobs = job_manager.get_jobs(state)
    if not jobs:
        print("No jobs found.")
        return
    print(f"Jobs (state: {state or 'all'}):")
    for j in jobs:
        print(f"- {j['id']} | {j['command']} | {j['state']}")


def status_summary():
    summary = job_manager.get_status_summary()
    print("Job Status Summary:")
    if not summary:
        print("  No jobs found.")
    else:
        for s, c in summary.items():
            print(f"  {s}: {c}")


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
