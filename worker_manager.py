import subprocess
import threading
import time
import job_manager
from helpers import load_config, exponential_backoff, log, sleep_for_delay

stop_flag = threading.Event()
workers_lock = threading.Lock()
active_workers = 0


def execute_job(job):
    try:
        result = subprocess.run(job["command"], shell=True, capture_output=True, text=True)
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
    config = load_config()
    max_retries = config.get("max_retries", 3)
    base = config.get("backoff_base", 2)

    new_attempts = job["attempts"] + 1
    job_manager.update_job_attempts(job["id"], new_attempts)
    job["attempts"] = new_attempts

    if job["attempts"] > max_retries:
        log(f"Job '{job['id']}' exceeded max retries. Moving to DLQ.")
        job_manager.move_to_dlq(job)
        return

    job_manager.update_job_state(job["id"], "failed")
    delay = exponential_backoff(base, job["attempts"])
    sleep_for_delay(delay)
    log(f"Retrying job '{job['id']}' (attempt {job['attempts']}).")
    job_manager.update_job_state(job["id"], "pending")

    all_jobs = job_manager.get_jobs()
    updated_job = None
    for j in all_jobs:
        if j["id"] == job["id"]:
            updated_job = j.copy()
            break

    if updated_job and not stop_flag.is_set():
        execute_job(updated_job)


def worker_loop(worker_id):
    global active_workers
    with workers_lock:
        active_workers += 1
    log(f"Worker {worker_id} started.")

    try:
        while not stop_flag.is_set():
            pending_jobs = job_manager.get_jobs("pending")
            if not pending_jobs:
                time.sleep(0.5)
                continue
            job = pending_jobs[0].copy()
            job_manager.update_job_state(job["id"], "processing")
            log(f"Worker {worker_id} is processing job '{job['id']}'.")
            execute_job(job)
    finally:
        with workers_lock:
            active_workers -= 1
        log(f"Worker {worker_id} stopped.")


def start_workers(count):
    global stop_flag
    stop_flag.clear()
    threads = []

    for i in range(count):
        t = threading.Thread(target=worker_loop, args=(i + 1,), daemon=True)
        t.start()
        threads.append(t)

    try:
        while any(t.is_alive() for t in threads):
            time.sleep(0.2)
    except KeyboardInterrupt:
        log("KeyboardInterrupt detected — stopping workers...")
        stop_workers()
        for t in threads:
            t.join()
        log("All workers stopped.")


def stop_workers():
    stop_flag.set()
    log("Stopping all workers...")


def get_active_workers_count():
    with workers_lock:
        return active_workers
