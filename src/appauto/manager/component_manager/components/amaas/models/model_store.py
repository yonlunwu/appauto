"""
将 ModelStore 作为一个对象, 可能分为多种 Model: ['llm', 'vlm', 'embedding', 'rerank', 'parser', 'audio']
"""

from functools import cached_property
from typing import List
from copy import deepcopy
from ....base_component import BaseComponent


class ModelStore(BaseComponent):
    OBJECT_TOKEN = "model_store_id"

    GET_URL_MAP = dict(
        list_model_stores="/v1/kllm/model-store",
        aaa="/v1/kllm/model-store/importable",
        bbb="/v1/kllm/model-store/import",
        ccc="/v1/kllm/model-store/{model_store_id}",
    )

    PUT_URL_MAP = dict(
        aaa="/v1/kllm/models/{model_id}",
    )

    POST_URL_MAP = dict(
        check="/v1/kllm/model-store/check",
        run="/v1/kllm/model-store/run",
        get_run_rule="/v1/kllm/model-store/get_run_rule",
    )

    DELETE_URL_MAP = dict(
        aaa="/v1/kllm/models/{model_id}",
    )

    def check(
        self,
        replicas=1,
        access_limit=4,
        max_total_tokens=8194,
        timeout=None,
        gpu_ids: List = None,
        tp: int = None,
        backend_parameters: List = None,
        hicache: int = 0,
        worker_id: int = None,
    ):
        # TODO max_token 最好能获取到 self, 因为每个 model 都不一样
        # TODO 新版本中 replica 只能是 1
        data = {
            "id": self.object_id,
            "replicas": replicas,
            "access_limit": access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [
                "--tensor-parallel-size",
                str(tp),
                "--max-total-tokens",
                str(max_total_tokens),
            ],
            "backend_parameters": backend_parameters or [],
        }

        if self.type in ["llm", "vlm"]:
            data["cache_storage"] = hicache

        if self.type in ["parser"]:
            fix_b_p = deepcopy(data["fixed_backend_parameters"])
            idx = fix_b_p.index("--max-total-tokens")
            fix_b_p.pop(idx)
            fix_b_p.pop(idx + 1)

        if worker_id is not None:
            data["worker_id"] = str(worker_id)

        return self.post("check", json_data=data, timeout=timeout)

    def run(
        self,
        replicas=1,
        access_limit=4,
        max_total_tokens=8194,
        timeout=None,
        gpu_ids: List = None,
        tp: int = None,
        backend_parameters: List = None,
        cache_storage: int = 0,
    ):
        data = {
            "id": self.object_id,
            "replicas": replicas,
            "access_limit": access_limit,
            "gpu_ids": gpu_ids,
            "fixed_backend_parameters": [
                "--tensor-parallel-size",
                str(tp),
                "--max-total-tokens",
                str(max_total_tokens),
            ],
            "backend_parameters": backend_parameters or [],
            "cache_storage": cache_storage,
        }
        return self.post("run", json_data=data, timeout=timeout)

    def get_run_rule(self, timeout=None):
        data = {"id": self.object_id}
        return self.post("get_run_rule", json_data=data, timeout=timeout)

    @cached_property
    def type(self):
        return self.data.type

    @cached_property
    def name(self):
        return self.data.name

    @property
    def source(self):
        return self.data.source

    @property
    def backend_type(self):
        return self.data.backend_type

    @property
    def local_path(self):
        return self.data.local_path

    @property
    def dir_path(self):
        return self.data.dir_path

    @property
    def weight_size(self):
        return self.data.weight_size

    @property
    def family(self):
        return self.data.family

    @property
    def quanted_type(self):
        return self.data.quanted_type

    @property
    def categories(self):
        return self.data.categories

    @property
    def required_vram(self):
        return self.data.required_vram

    @property
    def required_dram(self):
        return self.data.required_dram

    @property
    def required_disk(self):
        return self.data.required_disk

    @property
    def worker_name(self):
        return self.data.worker_name
