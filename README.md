# QueueCTL - Background Job Queue System

A simple job queue system built with Python. You can add jobs to a queue and workers will process them in the background. If a job fails, it will retry automatically. Jobs that fail too many times get moved to a dead letter queue.

## Table of Contents

1. [Setup Instructions](#1-setup-instructions)
2. [Usage Examples](#2-usage-examples)
3. [Architecture Overview](#3-architecture-overview)
4. [Testing Instructions](#4-testing-instructions)
5. [Demo Video](#5-demo-video)

---

## 5. Demo Video

Watch the demo video to see QueueCTL in action: [Demo Video Link](https://drive.google.com/file/d/1LjvGRFOpDAg3XvY6myNKqrVYdCicCML9/view?usp=sharing)

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

There's a file called `config.json` that controls how many times a job will retry if it fails. By default, jobs will retry 3 times before giving up. You can change this if you want.

---

## 2. Usage Examples

### Adding Jobs

To add a job to the queue, use the enqueue command with a JSON string:

```bash
python main.py enqueue '{"id": "job1", "command": "echo Hello World"}'
```

### Listing Jobs

List all jobs:

```bash
python main.py list
```

List jobs by state (pending, processing, completed, or dead):

```bash
python main.py list --state pending
python main.py list --state completed
python main.py list --state dead
```

### Checking Status

Get a summary of how many jobs are in each state:

```bash
python main.py status
```

### Running Workers

Start a single worker:

```bash
python main.py worker start
```

Start multiple workers:

```bash
python main.py worker start --count 3
```

Stop workers:

```bash
python main.py worker stop
```

You can also press Ctrl+C to stop workers while they're running.

---

## 3. Architecture Overview

### Job States

Jobs go through different states:
- **pending** - Waiting to be processed
- **processing** - Currently being run by a worker
- **completed** - Finished successfully
- **dead** - Failed after all retries, moved to dead letter queue

### Data Storage

Jobs are stored in JSON files:
- `jobs.json` - All jobs with their states and information
- `dlq.json` - Jobs that failed completely

### How It Works

Workers check for pending jobs every second. When they find one, they run it. If it succeeds, they mark it as completed. If it fails, they wait and try again. The wait time gets longer each time. After too many failures, the job goes to the dead letter queue.

You can run multiple workers at the same time. They all work independently and share the same job files safely.

---

## 4. Testing Instructions

### Basic Testing

Add a job and process it:

```bash
python main.py enqueue '{"id": "test1", "command": "echo Hello"}'
python main.py worker start
```

Check if it completed:

```bash
python main.py list --state completed
python main.py status
```

### Test Multiple Workers

Add several jobs and start multiple workers:

```bash
python main.py enqueue '{"id": "job1", "command": "sleep 2"}'
python main.py enqueue '{"id": "job2", "command": "sleep 2"}'
python main.py worker start --count 2
```

### Test Retries

Add a job that will fail:

```bash
python main.py enqueue '{"id": "fail_job", "command": "invalid_command"}'
python main.py worker start
```

Watch it retry and then check the dead letter queue:

```bash
python main.py list --state dead
```

### Check Files

You can look at the JSON files directly to see what's stored:

```bash
# On Linux/Mac
cat jobs.json
cat dlq.json

# On Windows
type jobs.json
type dlq.json
```

---

## File Structure

- `main.py` - Main entry point for commands
- `job_manager.py` - Handles job storage and retrieval
- `worker_manager.py` - Manages worker threads
- `helpers.py` - Utility functions
- `config.json` - Retry configuration
- `jobs.json` - Job storage (created automatically)
- `dlq.json` - Dead letter queue (created automatically)
