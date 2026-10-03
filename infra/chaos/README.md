# Chaos Mesh Experiments — LMS Resilience Testing

## Overview

This directory contains three Chaos Mesh experiments for validating the resilience of the LMS under real-world failure modes.

| File | Type | Target | Expected Outcome |
|------|------|--------|-----------------|
| `pod-chaos.yaml` | PodChaos | book-catalog | HPA + K8s self-healing restarts the killed pod within 30 s; catalog reads continue from surviving replicas |
| `network-chaos.yaml` | NetworkChaos | borrowing-service → user-svc | 500 ms latency injected on egress; borrowing-service 3 s timeout catches it; `/health` stays UP |
| `stress-chaos.yaml` | StressChaos | book-catalog | 90% CPU triggers HPA scale-out from 2 → up to 8 pods within ~2 min |

---

## Prerequisites

```bash
# 1. Install Chaos Mesh via Helm
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update

kubectl create namespace chaos-testing

helm install chaos-mesh chaos-mesh/chaos-mesh \
  --namespace chaos-testing \
  --version 2.6.3 \
  --set chaosDaemon.runtime=containerd \
  --set chaosDaemon.socketPath=/run/containerd/containerd.sock

# 2. Verify installation
kubectl get pods -n chaos-testing
```

---

## Running Experiments

### PodChaos — Book-Catalog Pod Failure

```bash
# Start
kubectl apply -f infra/chaos/pod-chaos.yaml

# Watch pods recover
kubectl get pods -l app=book-catalog -w

# Stop
kubectl delete -f infra/chaos/pod-chaos.yaml
```

**Expected behaviour:** One book-catalog pod enters `Terminating` / `Error` state each minute. K8s restarts it. HPA ensures at least 2 replicas always serve traffic.

---

### NetworkChaos — Borrowing → User-Service Latency

```bash
# Start
kubectl apply -f infra/chaos/network-chaos.yaml

# Test borrowing endpoint (should respond, possibly slower)
curl -s http://lms.local/api/borrow/active -H "Authorization: Bearer <token>"

# Stop
kubectl delete -f infra/chaos/network-chaos.yaml
```

**Expected behaviour:** Requests from borrowing-service to user-svc experience ~500 ms added delay. The 3-second `httpx` timeout is NOT breached. `/health` on borrowing-service stays `UP`.

---

### StressChaos — Book-Catalog CPU Spike (HPA Trigger)

```bash
# Ensure metrics-server is enabled on Minikube
minikube addons enable metrics-server

# Start stress
kubectl apply -f infra/chaos/stress-chaos.yaml

# Watch HPA scale out
kubectl get hpa book-catalog-hpa -w

# Stop
kubectl delete -f infra/chaos/stress-chaos.yaml
# Pods will scale back in after CPU normalises (~5 min cooldown)
```

**Expected behaviour:** CPU utilisation on book-catalog pods exceeds 70%. HPA scales from 2 → up to 8 replicas within ~90 s. After deleting the experiment, pods scale back to 2 within the HPA stabilization window.

---

## Chaos Mesh Dashboard (Optional)

```bash
kubectl port-forward -n chaos-testing svc/chaos-dashboard 2333:2333
# Open http://localhost:2333
```
