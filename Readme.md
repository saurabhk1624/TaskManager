# TaskManager API

A small FastAPI‑based backend for managing to‑do tasks.  
Tasks are persisted in MongoDB and, when created, an issue is optionally opened
in a GitHub repository via a background service.

---

## Features

* CRUD endpoints for tasks (`/tasks`)
* mark a task complete (`/tasks/{id}/complete`)
* MongoDB persistence via
  [`app.repository.task_repository.TaskRepository`](app/repository/task_repository.py)
* asynchronous GitHub integration
  via [`app.services.external_platform.GitHubExternalPlatformService`](app/services/external_platform.py)
* configuration via environment variables
  (`app/core/config.py` loads a `Settings` dataclass)
* containerised with Docker, runnable with `docker compose`
* Kubernetes manifests under `k8s/` for deployment

---

## Requirements

* Python 3.11+
* [docker](https://www.docker.com/) / [docker‑compose](https://docs.docker.com/compose/)
* (optional but needed for GitHub integration) a GitHub personal‑access token
  with `repo` permissions
* (for Kubernetes deployment) a cluster and `kubectl` access

---

## Environment

1. **Copy or create `.env`** at the project root; you may start from
   `.env.example` if one exists.

2. **Populate** with at least:

   ```env
   APP_NAME=task-manager
   APP_ENV=development
   LOG_LEVEL=debug
   PORT=8000

   # Mongo
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB_NAME=taskdb

   # GitHub integration
   GITHUB_TOKEN=<your-token>
   GITHUB_REPO=<owner/repo>



## Running the Project via Docker


   1.  Running locally with Docker Compose  Build and start the services:
    `docker compose up --build -d `
   2. Stop:
   `docker compose down`

The API is then available at http://localhost:8000. Use curl, httpie, or
FastAPI’s interactive docs to try it out.







## Kubernetes deployment
    The manifests in k8s describe the API, MongoDB, and required secrets.

1. Secrets
    Create a Kubernetes Secret containing the same environment variables you use
    locally. An example (secret.yaml) looks like:


    apiVersion: v1
    kind: Secret
    metadata:
    name: task-manager-secrets
    type: Opaque
    stringData:
    MONGO_URI: "mongodb://mongo-db:27017"
    MONGO_DB_NAME: "taskdb"
    GITHUB_TOKEN: "<your-token>"
    GITHUB_REPO: "owner/repo"

2. Apply it with:
    ```env
    minikube start --driver=docker
    eval $(minikube docker-env)
    docker build -t task-manager-api:latest .
    kubectl apply -f k8s/
    kubectl get pods
    minikube service task-manager-api