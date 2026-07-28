from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dispatcher import dispatch
from worker_manager import (
    register_worker,
    get_workers,
    remove_worker
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# MODELS
# -------------------------

class RegisterWorker(BaseModel):
    worker_id: str
    url: str
    capacity: int = 5


class StartMeeting(BaseModel):
    meeting_code: str
    passcode: str = ""
    bot_count: int
    duration_minutes: int = 5


# -------------------------
# ROOT
# -------------------------

@app.get("/")
async def root():
    return {
        "message": "Zoom Master Server Running",
        "status": "healthy"
    }


# -------------------------
# REGISTER WORKER
# -------------------------

@app.post("/register")
async def register(data: RegisterWorker):

    register_worker({
        "worker_id": data.worker_id,
        "url": data.url,
        "capacity": data.capacity,
        "online": True,
        "busy": False
    })

    return {
        "success": True,
        "message": "Worker Registered"
    }


# -------------------------
# START BOTS
# -------------------------

@app.post("/start")
async def start(data: StartMeeting):

    result = await dispatch(
        meeting_code=data.meeting_code,
        passcode=data.passcode,
        bot_count=data.bot_count,
        duration_minutes=data.duration_minutes
    )

    return result


# -------------------------
# ALL WORKERS
# -------------------------

@app.get("/workers")
async def workers():

    return get_workers()


# -------------------------
# REMOVE WORKER
# -------------------------

@app.delete("/worker/{worker_id}")
async def delete_worker(worker_id: str):

    remove_worker(worker_id)

    return {
        "success": True
    }


# -------------------------
# STATUS
# -------------------------

@app.get("/status")
async def status():

    workers = get_workers()

    online = len([w for w in workers if w.get("online")])
    busy = len([w for w in workers if w.get("busy")])

    return {
        "workers": len(workers),
        "online": online,
        "idle": online - busy,
        "busy": busy
    }
