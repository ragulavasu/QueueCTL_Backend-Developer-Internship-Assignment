# QueueCTL - Background Job Queue System

A simple job queue system built with Python. You can add jobs to a queue and workers will process them in the background. If a job fails, it will retry automatically. Jobs that fail too many times get moved to a dead letter queue.

## Table of Contents

1. [Setup Instructions](#1-setup-instructions)
2. [Usage Examples](#2-usage-examples)
3. [Architecture Overview](#3-architecture-overview)
4. [Assumptions & Trade-offs](#4-assumptions--trade-offs)
5. [Testing Instructions](#5-testing-instructions)

---

## 1. Setup Instructions

### Requirements

You need Python 3.8 or newer installed on your computer. The system works on Windows, Mac, or Linux. You don't need to install any extra libraries - everything uses Python's built-in features.

### Installation

First, get the code from the repository. Open your terminal and run:

```bash
git clone https://github.com/ragulavasu/QueueCTL_Backend-Developer-Internship-Assignment.git
cd QueueCTL_Backend-Developer-Internship-Assignment
```

Check if Python is installed by running `python --version` or `python3 --version`. If you see a version number, you're good to go.

That's it! No other setup needed. The system is ready to use.

### Configuration

There's a file called `config.json` that controls how many times a job will retry if it fails. By default, jobs will retry 3 times before giving up. You can change this if you want. The file also has a setting for how long to wait between retries - it uses something called exponential backoff, which means it waits longer each time.

---

## 2. Usage Examples

### Adding Jobs

To add a job to the queue, use the `enqueue` command. You need to provide a JSON string with an `id` and a `command`. The `id` is just a name for your job, and the `command` is what you want to run.

The command will show you a message confirming the job was added.

### Listing Jobs

You can see all your jobs using the `list` command. If you want to see only jobs in a specific state, you can add `--state` followed by the state you want to see. The states are: pending, processing, completed, or dead.

The list shows you the job ID, the command, the current state, and how many times it has been attempted.

### Checking Status

The `status` command gives you a quick summary of how many jobs are in each state. This is useful to see the overall picture of your queue.

### Running Workers

Workers are what actually process your jobs. You start them with the `worker start` command. You can run multiple workers at the same time by adding `--count` followed by a number.

Workers will keep running until you stop them. You can stop them with `worker stop` or by pressing Ctrl+C.

---

## 3. Architecture Overview

### How Jobs Move Through the System

When you add a job, it starts in the "pending" state. This means it's waiting in line to be processed. When a worker picks it up, it moves to "processing". 

If the job runs successfully, it becomes "completed". If it fails, the system will try again. It waits a bit longer each time before retrying. If it fails too many times (based on your config), it gets moved to the "dead" state and goes into something called the Dead Letter Queue, or DLQ for short.

### Where Data is Stored

Everything is saved in JSON files. There's a `jobs.json` file that keeps track of all your jobs - their state, how many times they've been tried, and when they were created or updated. There's also a `dlq.json` file that holds jobs that have completely failed.

The system uses file locking to make sure that when multiple workers are running at the same time, they don't mess up the data by writing to the files at the same time.

### How Workers Work

Each worker runs in its own thread. Workers check the queue every second to see if there are any pending jobs. When they find one, they grab it, mark it as processing, and run the command.

If the command succeeds, they mark it as completed. If it fails, they wait a bit and try again. The wait time gets longer each attempt - first 2 seconds, then 4, then 8, and so on. This is the exponential backoff I mentioned earlier.

You can run multiple workers at once, and they'll all work independently. Each one will grab jobs from the queue and process them. The file locking makes sure they don't step on each other.

---

## 4. Assumptions & Trade-offs

I made some decisions when building this system that you should know about:

**Using JSON files instead of a database**: This makes it simple and you don't need to set up anything extra. But it's not great if you need to handle thousands of jobs per second or run it across multiple computers.

**Using threads for workers**: This works well for running shell commands, which is what most jobs do. But if you had jobs that needed a lot of CPU power, Python's threading might not be the best choice.

**Checking for jobs every second**: Workers look for new jobs once per second. This means there might be a small delay before a job gets picked up, but it keeps the code simple and predictable.

**First in, first out**: Jobs are processed in the order they were added. There's no way to prioritize certain jobs or schedule them for later.

**Retries happen right away**: When a job fails, the worker waits and tries again before moving to the next job. This means the worker is busy during the wait time, but it makes sure the retry actually happens.

**Any command can be run**: Jobs can run any shell command. This is flexible, but you should be careful - don't let untrusted users add jobs, since they could run anything.

**No way to cancel jobs**: Once a job starts running, it will finish. You can't stop it partway through.

**All jobs are equal**: There's no priority system. Every job is treated the same.

**Single computer only**: All workers run in the same process on one machine. You can't spread this across multiple computers.

**No authentication**: Anyone who can access the files can add jobs. There's no security built in.

**No job results saved**: The system only tracks whether a job succeeded or failed, not what output it produced.

**No job dependencies**: You can't make one job wait for another job to finish first.

**No timeouts**: If a job runs forever, the worker will wait forever. There's no automatic timeout.

**Same job can be added multiple times**: The system doesn't check if a job with the same ID already exists.

---

## 5. Testing Instructions

### How to Test the System

To make sure everything works, you should try a few things:

**Test basic functionality**: Add a simple job, start a worker, and make sure it gets processed and marked as completed.

**Test multiple workers**: Add several jobs and start multiple workers. They should all work at the same time and process different jobs.

**Test retries**: Add a job that will fail (like a command that doesn't exist). Watch it retry a few times with increasing delays, then move to the dead letter queue.

**Test the dead letter queue**: After a job fails completely, check that it shows up in the dead jobs list and that the `dlq.json` file has it.

**Test status and listing**: Use the status command to see counts, and use the list command with different state filters to make sure filtering works.

**Test stopping workers**: Start some workers, then stop them. They should stop cleanly without errors.

**Test edge cases**: Try adding jobs with invalid JSON, or jobs missing required fields. The system should give you helpful error messages. Try starting workers when there are no jobs - they should just wait patiently.

You can also look at the JSON files directly to see what's stored. The `jobs.json` file has all jobs, and `dlq.json` has the failed ones. The `config.json` file has your retry settings.

If you want to start fresh for testing, you can clear the job files by replacing their contents with empty arrays.

---

## File Structure

The project has a few main files:

- `main.py` - This is where you run commands from
- `job_manager.py` - Handles saving and loading jobs
- `worker_manager.py` - Manages the worker threads that process jobs
- `helpers.py` - Some utility functions for config and logging
- `config.json` - Your retry settings
- `jobs.json` - Where jobs are stored (created automatically)
- `dlq.json` - Where failed jobs go (created automatically)

---

## Commands

Here are the commands you can use:

- `enqueue` - Add a job to the queue
- `list` - Show jobs, optionally filtered by state
- `status` - Show a summary of job counts by state
- `worker start` - Start workers to process jobs
- `worker stop` - Stop all workers

When adding a job, you need to provide JSON with at least an `id` and a `command`. The system will automatically add other fields like the state, attempt count, and timestamps.
