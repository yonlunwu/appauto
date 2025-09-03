"""
模型运行 - embedding
"""

from copy import deepcopy
from typing import List, Literal
from ..base import BaseModel, BaseModelStore


class EmbeddingModel(BaseModel):

    def __str__(self):
        return f"EmbeddingModel(Name: {self.name}, ID: {self.object_id})"

    def check(self, worker_id: int, tp: Literal[1, 2, 4, 8] = 1, gpu_ids: List = None, timeout=None):

        assert tp or gpu_ids

        b_p_list = deepcopy(self.backend_parameters)
        b_p_dict = {b_p_list[i]: b_p_list[i + 1] for i in range(0, len(b_p_list), 2)}

        b_p_dict["--tensor-parallel-size"] = "0" if gpu_ids else str(tp)

        data = {
            "id": self.model_store_id,
            "replicas": 1,
            "worker_id": str(worker_id),
            "access_limit": self.access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [],
            "backend_parameters": [item for k, v in b_p_dict.items() for item in (k, v)],
        }

        return self.post("check", url_map=BaseModelStore.POST_URL_MAP, json_data=data, timeout=timeout)

    def create_replica(self, worker_id: int, tp: Literal[1, 2, 4, 8] = 1, gpu_ids: List = None, timeout=None):

        assert tp or gpu_ids

        # 先获取所有副本
        before = self.instances

        b_p_list = deepcopy(self.backend_parameters)
        b_p_dict = {b_p_list[i]: b_p_list[i + 1] for i in range(0, len(b_p_list), 2)}

        b_p_dict["--tensor-parallel-size"] = "0" if gpu_ids else str(tp)
        data = {
            "model_id": self.object_id,
            "worker_id": str(worker_id),
            "gpu_ids": gpu_ids,
            "access_limit": self.access_limit,
            "backend_parameters": [item for k, v in b_p_dict.items() for item in (k, v)],
            "fixed_backend_parameters": [],
            "replicas": 1,
        }

        self.post("create_replica", json_data=data, timeout=timeout)

        # 再次获取所有副本
        return [ins for ins in self.instances if ins not in before][0]
