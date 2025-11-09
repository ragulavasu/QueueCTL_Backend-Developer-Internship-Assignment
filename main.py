import argparse
import json
import job_manager
import worker_manager
from helpers import set_config, get_config


def enqueue_job(job_json):
    try:
        job_data = json.loads(job_json)
    except json.JSONDecodeError:
        print("Invalid job JSON format.")
        return

    if "id" not in job_data or "command" not in job_data:
        print("Job must contain 'id' and 'command' fields.")
        return

    job_manager.add_job(job_data)
    print(f"Job '{job_data['id']}' added to the queue.")


def list_jobs(state=None):
    jobs = job_manager.get_jobs(state)
    if not jobs:
        print("No jobs found.")
        return
    print(f"Jobs (state: {state or 'all'}):")
    for j in jobs:
        print(f"- {j['id']} | {j['command']} | {j['state']} | attempts={j['attempts']}")


def status_summary():
    summary = job_manager.get_status_summary()
    active_workers = worker_manager.get_active_workers_count()
    print("Job Status Summary:")
    if not summary and active_workers == 0:
        print("  No jobs found.")
    else:
        for s, c in summary.items():
            print(f"  {s}: {c}")
        print(f"  Active Workers: {active_workers}")


def start_worker(count):
    print(f"Starting {count} worker(s)... Press Ctrl+C to stop.")
    worker_manager.start_workers(count)


def stop_worker():
    worker_manager.stop_workers()


def dlq_list():
    dlq_jobs = job_manager.get_dlq_jobs()
    if not dlq_jobs:
        print("Dead Letter Queue is empty.")
        return
    print("Dead Letter Queue:")
    for j in dlq_jobs:
        print(f"- {j['id']} | {j['command']} | attempts={j['attempts']}")


def dlq_retry(job_id):
    if job_manager.retry_dlq_job(job_id):
        print(f"Job '{job_id}' moved back to queue for retry.")
    else:
        print(f"Job '{job_id}' not found in Dead Letter Queue.")


def config_set(key, value):
    if set_config(key, value):
        print(f"Configuration updated: {key} = {value}")
    else:
        print(f"Invalid configuration key: {key}")


def config_get(key=None):
    if key:
        value = get_config(key)
        if value is not None:
            print(f"{key}: {value}")
        else:
            print(f"Invalid configuration key: {key}")
    else:
        config = get_config()
        print("Current Configuration:")
        print(f"  max-retries: {config.get('max_retries', 3)}")
        print(f"  backoff-base: {config.get('backoff_base', 2)}")


def main():
    parser = argparse.ArgumentParser(
        description="QueueCTL - Background Job Queue System"
    )
    subparsers = parser.add_subparsers(dest="command")

    enqueue_parser = subparsers.add_parser("enqueue", help="Add a new job to the queue")
    enqueue_parser.add_argument("job_json", help="Job JSON string")

    list_parser = subparsers.add_parser("list", help="List jobs by state")
    list_parser.add_argument("--state", help="Filter by state", required=False)

    subparsers.add_parser("status", help="Show summary of all job states")

    worker_parser = subparsers.add_parser("worker", help="Manage workers")
    worker_parser.add_argument("action", choices=["start", "stop"])
    worker_parser.add_argument("--count", type=int, default=1, help="Number of workers")

    dlq_parser = subparsers.add_parser("dlq", help="Dead Letter Queue operations")
    dlq_subparsers = dlq_parser.add_subparsers(dest="dlq_action")
    dlq_subparsers.add_parser("list", help="List all jobs in DLQ")
    dlq_retry_parser = dlq_subparsers.add_parser("retry", help="Retry a job from DLQ")
    dlq_retry_parser.add_argument("job_id", help="Job ID to retry")

    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_action")
    config_set_parser = config_subparsers.add_parser("set", help="Set configuration value")
    config_set_parser.add_argument("key", help="Configuration key (max-retries or backoff-base)")
    config_set_parser.add_argument("value", help="Configuration value")
    config_subparsers.add_parser("get", help="Get configuration value(s)")

    args = parser.parse_args()

    if args.command == "enqueue":
        enqueue_job(args.job_json)
    elif args.command == "list":
        list_jobs(args.state)
    elif args.command == "status":
        status_summary()
    elif args.command == "worker":
        if args.action == "start":
            start_worker(args.count)
        elif args.action == "stop":
            stop_worker()
    elif args.command == "dlq":
        if args.dlq_action == "list":
            dlq_list()
        elif args.dlq_action == "retry":
            dlq_retry(args.job_id)
    elif args.command == "config":
        if args.config_action == "set":
            config_set(args.key, args.value)
        elif args.config_action == "get":
            config_get()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
