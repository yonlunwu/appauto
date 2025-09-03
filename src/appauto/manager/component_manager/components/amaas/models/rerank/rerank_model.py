"""
模型运行 - vlm 模型
"""

from typing import Literal, List
from copy import deepcopy
from ..base import BaseModel, BaseModelStore
from ..model_instance import ModelInstance


class RerankModel(BaseModel):

    def __str__(self):
        return f"RerankModel(Name: {self.name}, ID: {self.object_id})"

    def check(
        self,
        worker_id: int,
        gpu_ids: List = None,
        tp: Literal[1, 2, 4, 8] = 1,
        timeout=None,
    ):
        from .rerank_model_store import RerankModelStore

        assert tp or gpu_ids

        b_p_list = deepcopy(self.backend_parameters)
        b_p_dict = {b_p_list[i]: b_p_list[i + 1] for i in range(0, len(b_p_list), 2)}

        b_p_dict["--tensor-parallel-size"] = "0" if gpu_ids else str(tp)

        data = {
            "id": self.model_store_id,
            "worker_id": str(worker_id),
            "gpu_ids": gpu_ids,
            "access_limit": self.access_limit,
            "backend_parameters": [item for k, v in b_p_dict.items() for item in (k, v)],
            "fixed_backend_parameters": [],  # fixed 在这里表示高级参数，v3.3.0 这个版本固定为 []
            "replicas": 1,  # v3.3.0 版本只能添加 1 个副本
        }

        return self.post("check", url_map=BaseModelStore.POST_URL_MAP, json_data=data, timeout=timeout)

    def create_replica(
        self,
        worker_id: int,
        tp: Literal[1, 2, 4, 8] = 1,
        gpu_ids: List = None,
        hicache: int = 0,
        wait_for_running=False,
        interval_s: int = 30,
        running_timeout_s: int = 600,
        timeout=None,
    ) -> ModelInstance:
        """
        - running_timeout_s: 等待 running 超时时间;
        - timeout: 单请求超时时间
        """
        assert tp or gpu_ids
        assert isinstance(hicache, int)

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
            "fixed_backend_parameters": [],  # fixed 在这里表示高级参数，v3.3.0 这个版本固定为 []
            "replicas": 1,  # v3.3.0 版本只能添加 1 个副本
            "cache_storage": hicache,
        }

        self.post("create_replica", json_data=data, timeout=timeout)

        ins = [ins for ins in self.instances if ins not in before][0]

        if wait_for_running:
            ins.wait_for_running(interval_s, running_timeout_s)

        return ins
