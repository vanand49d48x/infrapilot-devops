"""InfraPilot: read-only Kubernetes deployment health API."""

import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


def fetch_deployments():
    """Read deployments from the active kubectl context."""
    result = subprocess.run(
        ["kubectl", "get", "deployments", "--all-namespaces", "-o", "json"],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    return json.loads(result.stdout)


def analyze_deployments(data):
    """Summarize health of deployments, including rollouts and scaled-down workloads."""
    reports = []
    for item in data.get("items", []):
        metadata = item.get("metadata", {})
        spec = item.get("spec", {})
        status = item.get("status", {})

        desired = spec.get("replicas", 1)
        available = status.get("availableReplicas", 0)
        updated = status.get("updatedReplicas", 0)

        if desired == 0:
            health = "SCALED_DOWN"
        elif available < desired or updated < desired:
            health = "DEGRADED"
        else:
            health = "HEALTHY"

        reports.append({
            "name": metadata.get("name", "unknown"),
            "namespace": metadata.get("namespace", "default"),
            "desired": desired,
            "available": available,
            "updated": updated,
            "health": health,
        })
    return reports


class InfraPilotHandler(BaseHTTPRequestHandler):
    """Read-only HTTP endpoints for infrastructure visibility."""

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/health":
            return self.send_json(200, {
                "service": "InfraPilot",
                "status": "running",
                "version": "0.1.0",
            })
        if path == "/api/workloads":
            try:
                reports = analyze_deployments(fetch_deployments())
                return self.send_json(200, {
                    "total": len(reports),
                    "unhealthy": sum(r["health"] == "DEGRADED" for r in reports),
                    "deployments": reports,
                })
            except (FileNotFoundError, subprocess.CalledProcessError,
                    subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
                return self.send_json(503, {
                    "error": "Kubernetes cluster unavailable",
                    "details": type(exc).__name__,
                })
        return self.send_json(404, {"error": "Endpoint not found"})


def main():
    host = os.environ.get("INFRAPILOT_HOST", "127.0.0.1")
    port = int(os.environ.get("INFRAPILOT_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), InfraPilotHandler)
    print(f"InfraPilot API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
