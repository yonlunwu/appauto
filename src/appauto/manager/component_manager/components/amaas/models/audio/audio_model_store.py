from typing import List
from ..base.base_model_store import BaseModelStore


class AudioModelStore(BaseModelStore):

    def __str__(self):
        return f"AudioModelStore(Name: {self.name}, ID: {self.object_id})"

    def check(
        self,
        worker_id: int = None,
        tp: int = None,
        gpu_ids: List = None,
        access_limit=-1,
        backend_parameters: List = None,
        timeout=None,
    ):
        data = {
            "id": self.object_id,
            "replicas": 1,
            "worker_id": str(worker_id),
            "access_limit": access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [
                "--tensor-parallel-size",
                "0" if gpu_ids else str(tp),
                "--max-total-tokens",
                "30",
            ],
            "backend_parameters": backend_parameters or [],
        }

        return self.post("check", json_data=data, timeout=timeout)

    def run(
        self,
        worker_id: int = None,
        tp: int = None,
        gpu_ids: List = None,
        access_limit=-1,
        backend_parameters: List = None,
        timeout=None,
    ):
        data = {
            "id": self.object_id,
            "replicas": 1,
            "worker_id": str(worker_id),
            "access_limit": access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [
                "--tensor-parallel-size",
                "0" if gpu_ids else str(tp),
                "--max-total-tokens",
                "30",
            ],
            "backend_parameters": backend_parameters or [],
        }

        return self.post("run", json_data=data, timeout=timeout)
