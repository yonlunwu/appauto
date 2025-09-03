from typing import List
from ..base.base_model_store import BaseModelStore


class RerankModelStore(BaseModelStore):

    def __str__(self):
        return f"RerankModelStore(Name: {self.name}, ID: {self.object_id})"

    def check(
        self,
        worker_id: int = None,
        tp: int = None,
        gpu_ids: List = None,
        access_limit=-1,
        max_total_tokens=50000,
        backend_parameters: List = None,
        timeout=None,
    ):
        data = {
            "id": self.object_id,
            "replicas": 1,
            "access_limit": access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [
                "--tensor-parallel-size",
                "0" if gpu_ids else str(tp),
                "--max-total-tokens",
                str(max_total_tokens),
            ],
            "backend_parameters": backend_parameters or [],
            "worker_id": str(worker_id),
        }

        return self.post("check", json_data=data, timeout=timeout)

    def run(
        self,
        worker_id: int = None,
        tp: int = None,
        gpu_ids: List = None,
        access_limit=-1,
        max_total_tokens=50000,
        backend_parameters: List = None,
        timeout=None,
    ):
        data = {
            "id": self.object_id,
            "replicas": 1,
            "access_limit": access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [
                "--tensor-parallel-size",
                str(tp),
                "--max-total-tokens",
                str(max_total_tokens),
            ],
            "backend_parameters": backend_parameters or [],
            "worker_id": str(worker_id),
        }

        return self.post("run", json_data=data, timeout=timeout)
