import time
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel

app = FastAPI(title="TaskManagerAPI", version="1.0.0")

# --- MÉTRIQUES PROMETHEUS ---
# Compteur du nombre de tâches créées
TASKS_CREATED_TOTAL = Counter(
    "task_manager_tasks_created_total",
    "Nombre total de tâches créées dans l'API",
    ["priority"],
)
# Histogramme pour mesurer la latence des requêtes
REQUEST_LATENCY = Histogram(
    "task_manager_request_latency_seconds",
    "Latence des requêtes HTTP en secondes",
    ["method", "endpoint"],
)


# --- MODÈLES DE DONNÉES ---
class Task(BaseModel):
    id: int
    title: str
    priority: str  # low, medium, high
    completed: bool = False


# Base de données temporaire en mémoire
tasks_db: List[Task] = []


# --- ENDPOINTS ---

# 1. Endpoint /health (Obligatoire)
@app.get("/health")
def health():
    start_time = time.time()
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(method="GET", endpoint="/health").observe(latency)
    return {"status": "ok"}


# 2. Endpoint /metrics pour Prometheus
@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# 3. Créer une tâche (POST)
@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: Task):
    start_time = time.time()

    # Vérification si l'ID existe déjà
    if any(t.id == task.id for t in tasks_db):
        raise HTTPException(status_code=400, detail="Task ID already exists")

    tasks_db.append(task)

    # Incrémentation de la métrique custom avec le label de priorité
    if task.priority in ["low", "medium", "high"]:
        TASKS_CREATED_TOTAL.labels(priority=task.priority).inc()
    else:
        TASKS_CREATED_TOTAL.labels(priority="unknown").inc()

    latency = time.time() - start_time
    REQUEST_LATENCY.labels(method="POST", endpoint="/tasks").observe(latency)
    return task


# 4. Lister les tâches (GET)
@app.get("/tasks", response_model=List[Task])
def get_tasks():
    start_time = time.time()
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(method="GET", endpoint="/tasks").observe(latency)
    return tasks_db