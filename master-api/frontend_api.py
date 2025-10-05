import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json, uuid, os

# Create the router instance
router = APIRouter()

ORCHESTRATOR_URL = "http://127.0.0.1:9000/orchestrator/orchestrate"


# Define the expected request body
class DataFormat(BaseModel):
    lat: float
    long: float
    prediction_hours: int = 24  # Frontend specifies this directly


def load_data():
    if not os.path.exists("processes.txt"):  # Changed from processes.json
        return []
    with open("processes.txt", "r") as f:
        return json.load(f)


def save_data(data):
    with open("processes.txt", "w") as f:  # Changed from processes.json
        json.dump(data, f, indent=4)


@router.post("/submit")
def submit_data(req: DataFormat):
    processes = load_data()
    task_id = str(uuid.uuid4())

    new_entry = {"id": task_id, "done": False}
    processes.append(new_entry)
    save_data(processes)

    # THIS IS THE MISSING PIECE - trigger orchestration
    payload = {"id": task_id, "lat": req.lat, "long": req.long, "prediction_hours": req.prediction_hours}

    try:
        requests.post(ORCHESTRATOR_URL, json=payload, timeout=2)
    except Exception as e:
        print(f"Warning: Could not contact orchestrator: {e}")

    return {"task_id": task_id, "status": "queued"}


# ADD THIS ENDPOINT
@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    """Check the status of a task by its ID"""
    processes = load_data()

    for task in processes:
        if task["id"] == task_id:
            return task

    # Task not found
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# OPTIONAL: Add this to list all tasks
@router.get("/tasks")
def get_all_tasks():
    """Get all tasks"""
    return {"tasks": load_data()}
