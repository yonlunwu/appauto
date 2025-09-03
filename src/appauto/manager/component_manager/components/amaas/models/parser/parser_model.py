"""
模型运行 - parser 模型
"""

from typing import List, Literal
from ..base import BaseModel, BaseModelStore
from ..model_instance import ModelInstance


class ParserModel(BaseModel):

    def __str__(self):
        return f"ParserModel(Name: {self.name}, ID: {self.object_id})"

    def check(self, worker_id: int, gpu_ids: List = None, tp: Literal[1, 2, 4, 8] = 1, timeout=None):

        assert tp or gpu_ids

        data = {
            "id": self.model_store_id,
            "replicas": 1,
            "worker_id": str(worker_id),
            "access_limit": self.access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [],
            "backend_parameters": ["--tensor-parallel-size", "0" if gpu_ids else str(tp)],
        }

        return self.post("check", url_map=BaseModelStore.POST_URL_MAP, json_data=data, timeout=timeout)

    def create_replica(
        self,
        worker_id: int,
        gpu_ids: List = None,
        tp: Literal[1, 2, 4, 8] = 1,
        timeout=None,
    ) -> ModelInstance:

        assert tp or gpu_ids

        # 先获取所有副本
        before = self.instances

        data = {
            "model_id": self.object_id,
            "replicas": 1,
            "worker_id": str(worker_id),
            "access_limit": self.access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [],
            "backend_parameters": ["--tensor-parallel-size", "0" if gpu_ids else str(tp)],
        }

        self.post("create_replica", json_data=data, timeout=timeout)

        return [ins for ins in self.instances if ins not in before][0]
