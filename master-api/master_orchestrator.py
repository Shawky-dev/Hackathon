from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
import json, os, requests

router = APIRouter()
FILEE = "processes.txt"
DATA_FETCH_URL = "http://127.0.0.1:8000/data/past-data"
AI_NODE_URL = "http://127.0.0.1:8002/predict"


class TaskPayload(BaseModel):
    id: str
    lat: float
    long: float
    prediction_hours: int = 24  # How many hours to predict into the future


def load_data():
    if not os.path.exists(FILEE):
        return []
    with open(FILEE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_data(data):
    with open(FILEE, "w") as f:
        json.dump(data, f, indent=4, default=str)


def update_task_status(task_id: str, done: bool, result=None):
    processes = load_data()
    for task in processes:
        if task["id"] == task_id:
            task["done"] = done
            if result:
                task["result"] = result
            break
    save_data(processes)


def process_task(task_id: str, lat: float, long: float, prediction_hours: int):
    try:
        # Fetch historical data (168 hours for model training)
        data_response = requests.get(DATA_FETCH_URL, params={"hours": 168, "lat": lat, "long": long}, timeout=300)

        if data_response.status_code != 200:
            update_task_status(task_id, True, {"error": "Data fetch failed"})
            return

        fetched_data = data_response.json()

        # Send to AI node with prediction_hours
        ai_payload = {"task_id": task_id, "lat": lat, "long": long, "historical_data": fetched_data, "prediction_hours": prediction_hours}  # Pass it to AI

        ai_response = requests.post(AI_NODE_URL, json=ai_payload, timeout=300)
        ai_result = ai_response.json()

        update_task_status(task_id, True, ai_result)

    except Exception as e:
        print(f"Error processing task {task_id}: {e}")
        update_task_status(task_id, True, {"error": str(e)})


@router.post("/orchestrate")
def orchestrate_task(payload: TaskPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_task, payload.id, payload.lat, payload.long, payload.prediction_hours)  # Pass prediction_hours
    return {"status": "processing", "task_id": payload.id}