# enricher.py


class EventEnricher:
    def __init__(self, k8s_client):
        self.k8s_client = k8s_client

    def enrich_event(self, pid):
        """Fetch Kubernetes metadata related to the process PID."""
        pod_list = self.k8s_client.list_pod_for_all_namespaces(watch=False)
        for pod in pod_list.items:
            for container in pod.status.container_statuses:
                if container.container_id and str(pid) in container.container_id:
                    return {
                        "namespace": pod.metadata.namespace,
                        "pod_name": pod.metadata.name,
                        "node_name": pod.spec.node_name,
                    }
        return {}
