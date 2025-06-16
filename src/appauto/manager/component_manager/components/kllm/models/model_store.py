"""
将 ModelStore 作为一个对象, 可能分为多种 Model: ['llm', 'vlm', 'embedding', 'rerank', 'parser', 'audio']
"""

import json
from ....base_component import BaseComponent


# TODO 要继承 BaseComponent
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
        return self.raw_post("check", json=data, timeout=timeout)

    def run(self, gpu_count=1, replicas=1, access_limit=1, max_token=8194, timeout=None):
        data = {
            "gpu_count": gpu_count,
            "replicas": replicas,
            "access_limit": access_limit,
            "max_input_length": max_token,
            "id": self.object_id,
            "backend_parameters": ["--tensor-parallel-size", "1", "--max-total-tokens", str(max_token)],
        }
        return self.raw_post("run", json=data, timeout=timeout)
