from vca_core.interfaces.worker_client import WorkerClientProtocol
from vca_infra.gateways import CeleryWorkerClient


def get_worker_client() -> WorkerClientProtocol:
    """WorkerClientを提供する."""
    return CeleryWorkerClient()
