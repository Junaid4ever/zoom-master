import json
import os
from threading import Lock

WORKERS_FILE = "workers.json"

lock = Lock()


def _ensure_file():
    if not os.path.exists(WORKERS_FILE):
        with open(WORKERS_FILE, "w") as f:
            json.dump([], f)


def get_workers():
    _ensure_file()

    with lock:
        with open(WORKERS_FILE, "r") as f:
            return json.load(f)


def save_workers(workers):
    with lock:
        with open(WORKERS_FILE, "w") as f:
            json.dump(workers, f, indent=4)


def register_worker(worker):
    workers = get_workers()

    for i, w in enumerate(workers):
        if w["worker_id"] == worker["worker_id"]:
            workers[i] = worker
            save_workers(workers)
            return

    workers.append(worker)
    save_workers(workers)


def remove_worker(worker_id):
    workers = get_workers()

    workers = [w for w in workers if w["worker_id"] != worker_id]

    save_workers(workers)


def update_worker(worker_id, **kwargs):
    workers = get_workers()

    for worker in workers:
        if worker["worker_id"] == worker_id:
            worker.update(kwargs)

    save_workers(workers)


def get_online_workers():
    workers = get_workers()

    return [
        worker
        for worker in workers
        if worker.get("online", False)
    ]


def get_idle_workers():
    workers = get_workers()

    return [
        worker
        for worker in workers
        if worker.get("online", False)
        and worker.get("busy", False) is False
    ]


def mark_busy(worker_id):
    update_worker(worker_id, busy=True)


def mark_idle(worker_id):
    update_worker(worker_id, busy=False)
