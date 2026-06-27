from fastapi.testclient import TestClient
from src.main import app, tasks_db

client = TestClient(app)

# Avant chaque test, on vide la base de données en mémoire
def setup_function():
    tasks_db.clear()

# Test 1 : Vérification de l'endpoint de santé /health (Retourne 200 OK)
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Test 2 : Création réussie d'une tâche (Retourne 201 Created)
def test_create_task_success():
    task_data = {"id": 1, "title": "Configurer le pipeline Jenkins", "priority": "high", "completed": False}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    assert response.json()["title"] == "Configurer le pipeline Jenkins"
    assert response.json()["priority"] == "high"

# Test 3 : Rejet si l'identifiant de la tâche existe déjà (Retourne 400 Bad Request)
def test_create_task_duplicate_id_fails():
    task_data = {"id": 99, "title": "Tâche doublon", "priority": "low", "completed": False}
    # Premier ajout
    client.post("/tasks", json=task_data)
    # Deuxième ajout avec le même ID
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Task ID already exists"