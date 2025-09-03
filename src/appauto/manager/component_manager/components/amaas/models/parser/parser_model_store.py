from typing import List
from time import sleep
from ..base.base_model_store import BaseModelStore
from .parser_model import ParserModel


class ParserModelStore(BaseModelStore):

    def __str__(self):
        return f"ParserModelStore(Name: {self.name}, ID: {self.object_id})"

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
            "fixed_backend_parameters": ["--tensor-parallel-size", "0" if gpu_ids else str(tp)],
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
        wait_for_running=False,
        interval_s: int = 30,
        running_timeout_s: int = 600,
        timeout=None,
    ) -> ParserModel:
        assert not [m for m in self.amaas.model.parser if m.name == self.name]
        data = {
            "id": self.object_id,
            "replicas": 1,
            "worker_id": str(worker_id),
            "access_limit": access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": ["--tensor-parallel-size", "0" if gpu_ids else str(tp)],
            "backend_parameters": backend_parameters or [],
        }

        self.post("run", json_data=data, timeout=timeout)

        sleep(1)
        model = [m for m in self.amaas.model.parser if m.name == self.name][0]

        if wait_for_running:
            model.wait_for_running(interval_s, running_timeout_s)

        return model
