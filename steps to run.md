# 🚀 Steps to Run & Verify the Library Management System (LMS)

This guide provides step-by-step instructions to run, navigate, and verify the LMS microservices platform using Docker Compose and Kubernetes.

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Quick Start (Docker Compose)](#2-quick-start-docker-compose)
3. [Service URLs & Ports](#3-service-urls--ports)
4. [Demo Accounts](#4-demo-accounts)
5. [Step-by-Step UI Guide](#5-step-by-step-ui-guide)
   - [A. Log In](#a-log-in)
   - [B. Explore & Search the Catalog](#b-explore--search-the-catalog)
   - [C. Circulation (Checkout & Return)](#c-circulation-checkout--return)
   - [D. Member Management & Stats](#d-member-management--stats)
   - [E. Transactional Emails (MailHog)](#e-transactional-emails-mailhog)
6. [Interactive Swagger API Documentation](#6-interactive-swagger-api-documentation)
7. [Direct Database & Cache Verification](#7-direct-database--cache-verification)
8. [Kubernetes (Minikube) Deployment](#8-kubernetes-minikube-deployment)
9. [Chaos Engineering Experiments](#9-chaos-engineering-experiments)
10. [Troubleshooting & Maintenance Commands](#10-troubleshooting--maintenance-commands)

---

## 1. Prerequisites
- **Docker Desktop** (running on Windows with WSL2 or Hyper-V backend)
- **PowerShell** or **Git Bash**
- Optional (for K8s mode): **Minikube** + **kubectl** + **Helm**

---

## 2. Quick Start (Docker Compose)

### Step 1: Open Terminal in Project Directory
```powershell
cd "C:\Users\Sunil Choubey\Downloads\Accl project"
```

### Step 2: Ensure Environment File Exists
```powershell
# Copy example env file if .env does not already exist
Copy-Item .env.example .env -Force
```

### Step 3: Build and Start All Containers
```powershell
docker compose up --build -d
```

### Step 4: Verify Container Health
```powershell
docker compose ps
```
All containers should display status `healthy` or `running`.

---

## 3. Service URLs & Ports

| Service | Port / Address | Health Probe | Description |
|---|---|---|---|
| 🌐 **Frontend** | [http://localhost:3000](http://localhost:3000) | `GET /` | Next.js Librarian & Member Portal |
| 📚 **Book Catalog** | [http://localhost:5001](http://localhost:5001) | `GET /health` | FastAPI + Redis Caching |
| 👤 **User Service** | [http://localhost:5002](http://localhost:5002) | `GET /health` | FastAPI + JWT + Bcrypt Auth |
| 📋 **Borrowing Service** | [http://localhost:5003](http://localhost:5003) | `GET /health` | FastAPI + Inter-service Client |
| 🔔 **Notification Service** | [http://localhost:5004](http://localhost:5004) | `GET /health` | FastAPI + SMTP Dispatch |
| 📧 **MailHog Web UI** | [http://localhost:8025](http://localhost:8025) | — | View sent transactional emails |
| 🐘 **PostgreSQL 15** | `localhost:5432` | `pg_isready` | Relational database (schema preloaded) |
| ⚡ **Redis 7** | `localhost:6379` | `redis-cli ping` | In-memory cache & JWT token blacklist |

---

## 4. Demo Accounts

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Librarian** | `librarian@library.org` | `admin123` | Full Access: Circulation, All Members, System Stats, Inventory CRUD |
| **Member** | `alice@library.org` | `user123` | Member: Catalog Search, Checkout, Active Loans, Return |
| **Member** | `bob@library.org` | `user123` | Member: Catalog Search, Checkout, Active Loans, Return |

---

## 5. Step-by-Step UI Guide

### A. Log In
1. Open your browser and navigate to **[http://localhost:3000](http://localhost:3000)**.
2. In the top navigation bar:
   - Enter **Email:** `librarian@library.org`
   - Enter **Password:** `admin123`
   - Click **Login**.
3. You will see your name `Elena Vance (Chief Librarian)` and a role badge `LIBRARIAN` displayed in the header.

---

### B. Explore & Search the Catalog
1. Click the **Catalog** tab.
2. Use the search input to filter books by keyword:
   - Example search: `Design` or `Clean`
3. Filter by genre:
   - Example genre: `Computer Science` or `Cloud Computing`
4. Toggle **Available only** to filter out books that currently have 0 available copies.
5. Take note of any book's ID and stock:
   - Example: *Clean Architecture* (ID: 3) — Available copies: 5.

---

### C. Circulation (Checkout & Return)
1. Click the **Circulation** tab.

#### How to Checkout a Book:
1. Under the **Checkout Book** form:
   - **Book ID:** Enter the ID of the book (e.g. `3`)
   - **Due Date:** Pick a future date (e.g. `2026-12-15`)
2. Click **Checkout**.
3. You will receive a success banner: `✅ Checked out! Record #<id>`.
4. In the **Active Loans** table below, your new loan will appear.
5. In the **Catalog** tab, the available copies for book #3 will have decreased by 1.

#### How to Return a Book:
1. In the **Active Loans** table, find the **Record #** (e.g., `1` for Alice's initial seed loan, or the ID generated from your checkout).
2. Under the **Return Book** card:
   - **Record ID:** Enter the record number.
3. Click **Return**.
4. You will see: `✅ Returned! Fine: $0.00` (or the accrued fine if overdue).
5. The book will disappear from **Active Loans**, and stock in the catalog will increment back.

---

### D. Member Management & Stats
1. Log in as a librarian (`librarian@library.org`).
2. Click the **Members** tab.
3. You will see:
   - **Active Loans Metric:** Total currently borrowed books across the library.
   - **Overdue Metric:** Total overdue items.
   - **Returned Metric:** Lifetime returned loans.
   - **Member Directory:** Full table of registered members, emails, roles, and membership join dates.

---

### E. Transactional Emails (MailHog)
Whenever a checkout or return occurs, the notification service sends an HTML email:
1. Open **[http://localhost:8025](http://localhost:8025)**.
2. You will see emails sent in real time:
   - Subject: `Checkout Confirmation: <Book Title>`
   - Subject: `Return Confirmation: <Book Title>`
3. Click any email to view the rendered HTML receipt with due dates, record IDs, and fine details.

---

## 6. Interactive Swagger API Documentation

Each FastAPI backend exposes an interactive OpenAPI Swagger interface:
- **Book Catalog Docs:** [http://localhost:5001/docs](http://localhost:5001/docs)
- **User & Auth Docs:** [http://localhost:5002/docs](http://localhost:5002/docs)
- **Borrowing Docs:** [http://localhost:5003/docs](http://localhost:5003/docs)
- **Notification Docs:** [http://localhost:5004/docs](http://localhost:5004/docs)

Prometheus metrics can be inspected directly on any service at:
- `http://localhost:5001/metrics`
- `http://localhost:5002/metrics`
- `http://localhost:5003/metrics`
- `http://localhost:5004/metrics`

---

## 7. Direct Database & Cache Verification

### Inspect Database Tables via CLI
```powershell
# View all borrow records
docker exec -it lms-postgres psql -U lms_user -d lms_db -c "SELECT id, book_id, member_id, due_date, status, fine_amount FROM borrow_records;"

# View all catalog books & stock
docker exec -it lms-postgres psql -U lms_user -d lms_db -c "SELECT id, title, available_copies, total_copies FROM books LIMIT 10;"

# View notification audit log
docker exec -it lms-postgres psql -U lms_user -d lms_db -c "SELECT id, recipient_email, message_type, content, status FROM notifications_log;"
```

### Inspect Redis Cache Keys
```powershell
docker exec -it lms-redis redis-cli KEYS "*"
```

---

## 8. Kubernetes (Minikube) Deployment

To run the complete platform on a local Kubernetes cluster:

```powershell
# 1. Start Minikube
minikube start --cpus=4 --memory=8192

# 2. Enable necessary addons
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Direct Docker CLI to Minikube's Docker daemon
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# 4. Build images inside Minikube
docker build -t lms/book-catalog:latest ./book-catalog
docker build -t lms/user-service:latest ./user-service
docker build -t lms/borrowing-service:latest ./borrowing-service
docker build -t lms/notification-service:latest ./notification-service
docker build -t lms/frontend:latest ./frontend

# 5. Apply declarative manifests
kubectl apply -f infra/k8s/

# 6. Verify pods & services
kubectl get pods
kubectl get hpa
kubectl get ingress

# 7. Access Frontend via NodePort or Minikube tunnel
minikube service frontend-svc
```

---

## 9. Chaos Engineering Experiments

The system includes preconfigured Chaos Mesh experiments in `infra/chaos/`:

```powershell
# Install Chaos Mesh (requires Helm)
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update
kubectl create namespace chaos-testing
helm install chaos-mesh chaos-mesh/chaos-mesh --namespace chaos-testing

# 1. Pod Failure Chaos (kills book-catalog pod every 60s to test self-healing)
kubectl apply -f infra/chaos/pod-chaos.yaml

# 2. Network Latency Chaos (adds 500ms latency to test 3s resilience timeout)
kubectl apply -f infra/chaos/network-chaos.yaml

# 3. CPU Stress Chaos (spikes CPU to test Horizontal Pod Autoscaler scale-out)
kubectl apply -f infra/chaos/stress-chaos.yaml

# Stop all experiments
kubectl delete -f infra/chaos/
```

---

## 10. Troubleshooting & Maintenance Commands

### Restart a specific service after edits
```powershell
docker compose up -d --build <service-name>
# Example: docker compose up -d --build borrowing-service
```

### Tail logs of a specific service
```powershell
docker compose logs -f book-catalog
docker compose logs -f user-service
docker compose logs -f borrowing-service
docker compose logs -f frontend
```

### Reset database and cache volumes
```powershell
docker compose down -v
docker compose up --build -d
```

### Stop all containers
```powershell
docker compose down
```
