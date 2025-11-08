import subprocess
import threading
import time
import job_manager
from helpers import load_config, exponential_backoff, log, sleep_for_delay


stop_flag = False


def execute_job(job):
    """Run the given job's shell command."""
    try:
        result = subprocess.run(
            job["command"], shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            log(f"Job '{job['id']}' completed successfully.")
            job_manager.update_job_state(job["id"], "completed")
        else:
            log(f"Job '{job['id']}' failed with return code {result.returncode}.")
            handle_failed_job(job)
    except Exception as e:
        log(f"Error executing job '{job['id']}': {e}")
        handle_failed_job(job)


def handle_failed_job(job):
    """Handle job retry or move to DLQ."""
    config = load_config()
    max_retries = config.get("max_retries", 3)
    base = config.get("backoff_base", 2)

    job["attempts"] += 1

    if job["attempts"] > max_retries:
        log(f"Job '{job['id']}' exceeded max retries. Moving to DLQ.")
        job_manager.move_to_dlq(job)
        job_manager.update_job_state(job["id"], "dead")
        return

    delay = exponential_backoff(base, job["attempts"])
    sleep_for_delay(delay)
    log(f"Retrying job '{job['id']}' (attempt {job['attempts']}).")
    execute_job(job)


def worker_loop(worker_id):
    """Worker thread loop that continuously fetches and executes jobs."""
    global stop_flag
    log(f"Worker {worker_id} started.")
    while not stop_flag:
        pending_jobs = job_manager.get_jobs("pending")
        if not pending_jobs:
            time.sleep(1)
            continue
        job = pending_jobs[0]
        job_manager.update_job_state(job["id"], "processing")
        log(f"Worker {worker_id} is processing job '{job['id']}'.")
        execute_job(job)
    log(f"Worker {worker_id} stopped.")


def start_workers(count):
    """Start multiple worker threads."""
    threads = []
    for i in range(count):
        t = threading.Thread(target=worker_loop, args=(i + 1,))
        t.start()
        threads.append(t)
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        stop_workers()


def stop_workers():
    """Gracefully stop all workers."""
    global stop_flag
    stop_flag = True
    log("Stopping all workers...")
