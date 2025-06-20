"""
将 ModelStore 作为一个对象, 可能分为多种 Model: ['llm', 'vlm', 'embedding', 'rerank', 'parser', 'audio']
"""

from functools import cached_property
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
    )

    DELETE_URL_MAP = dict(
        aaa="/v1/kllm/models/{model_id}",
    )

    def check(self, replicas=1, access_limit=1, max_token=8194, timeout=None):
        # TODO max_token 最好能获取到 self, 因为每个 model 都不一样
        data = {
            "id": self.object_id,
            "replicas": replicas,
            "access_limit": access_limit,
            "backend_parameters": ["--tensor-parallel-size", "1", "--max-total-tokens", str(max_token)],
        }
        return self.post("check", json=data, timeout=timeout)

    def run(self, gpu_count=1, replicas=1, access_limit=1, max_token=8194, timeout=None):
        data = {
            "gpu_count": gpu_count,
            "replicas": replicas,
            "access_limit": access_limit,
            "max_input_length": max_token,
            "id": self.object_id,
            "backend_parameters": ["--tensor-parallel-size", "1", "--max-total-tokens", str(max_token)],
        }
        return self.post("run", json=data, timeout=timeout)

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
