"""Unit tests for deployment health summaries."""

import unittest
from main import analyze_deployments


class TestDeploymentHealth(unittest.TestCase):
    def test_healthy_deployment(self):
        data = {"items": [{
            "metadata": {"name": "web-api", "namespace": "production"},
            "spec": {"replicas": 3},
            "status": {"availableReplicas": 3, "updatedReplicas": 3},
        }]}
        result = analyze_deployments(data)
        self.assertEqual(result[0]["health"], "HEALTHY")
        self.assertEqual(result[0]["available"], 3)

    def test_degraded_deployment(self):
        data = {"items": [{
            "metadata": {"name": "payment-service"},
            "spec": {"replicas": 4},
            "status": {"availableReplicas": 1},
        }]}
        self.assertEqual(analyze_deployments(data)[0]["health"], "DEGRADED")

    def test_scaled_down_deployment(self):
        data = {"items": [{
            "metadata": {"name": "worker"},
            "spec": {"replicas": 0},
            "status": {},
        }]}
        self.assertEqual(analyze_deployments(data)[0]["health"], "SCALED_DOWN")

    def test_empty_cluster(self):
        self.assertEqual(analyze_deployments({"items": []}), [])


if __name__ == "__main__":
    unittest.main()
