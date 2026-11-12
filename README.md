# InfraPilot

**Cloud-native DevOps automation and infrastructure reliability platform**

InfraPilot is an open-source project focused on infrastructure visibility, deployment reliability, Kubernetes operations, and safe remediation workflows.

## Status

Early development. The first working component is a read-only Kubernetes deployment health API.

## Implemented

- `GET /api/health`: service health check
- `GET /api/workloads`: summarize Kubernetes deployments across namespaces
- Deployment states: `HEALTHY`, `DEGRADED`, `SCALED_DOWN`
- Basic error reporting when `kubectl` or Kubernetes is unavailable
- Unit tests for health classification

## Roadmap

- [ ] Kubernetes event and incident ingestion
- [ ] Deployment history and rollout tracking
- [ ] Policy-based remediation suggestions and human approvals
- [ ] Incident audit trail and persistent storage
- [ ] Metrics and tracing integration
- [ ] GitOps and CI/CD integration
- [ ] Multi-cluster dashboard
- [ ] Infrastructure drift detection

## Getting started

Requirements: Python 3.9+; `kubectl` and a configured Kubernetes context for workload inspection.

From the repository root, run:

```bash
python3 -m unittest discover -s backend -v
python3 backend/main.py
```

In another terminal:

```bash
curl http://localhost:8080/api/health
curl http://localhost:8080/api/workloads
```

The health endpoint works without Kubernetes. The workloads endpoint uses the current `kubectl` context and requires permission to list deployments across namespaces. On an unavailable cluster, it returns HTTP 503.

By default, the API listens on `127.0.0.1:8080`. Configure `INFRAPILOT_HOST` and `INFRAPILOT_PORT` to change the binding. Do not expose this development server publicly without authentication and authorization.

## Architecture direction

The planned platform will separate infrastructure discovery, state reconciliation, incident detection, and controlled remediation into independently testable components. Operational changes will be guarded by policy checks, approvals, and audit records.
