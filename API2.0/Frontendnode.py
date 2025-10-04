from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json, uuid, os, requests


app=FastAPI()
FILEE="processes.txt"
MASTER_NODE_URL = "http://127.0.0.1:9000/receive"  # Master node endpoint

class DataFormat(BaseModel):
    lat: float
    long: float
    date: datetime

def load_data():
    if not os.path.exists(FILEE):
        return[]
    with open(FILEE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return[]
        
def save_data(data):
    with open(FILEE, "w") as f:
        json.dump(data, f, indent=4, default=str)

@app.post("/submit")
def submit_data(req:DataFormat):
    processes= load_data()
    task_id=str(uuid.uuid4())

    new_entry = {
        "id": task_id,
        "done": False
    }
    processes.append(new_entry)
    save_data(processes)
    

    payload = {
        "id": task_id,
        "lat": req.lat,
        "long": req.long,
        "date": req.date.isoformat()
    }

    try:
        requests.post(MASTER_NODE_URL, json=payload, timeout=2)
    except Exception as e:
        print(f"Warning: Could not contact master node: {e}")

    return {"task_id": task_id, "status": "queued"}

@app.get("/tasks")
def get_all_tasks():
    return load_data()

@app.get("/status/{task_id}")
def check_task_status(task_id: str):
    processes = load_data()
    for task in processes:
        if task["id"] == task_id:
            return {"task_id": task_id, "done": task["done"]}
    return {"error": "Task not found"}
