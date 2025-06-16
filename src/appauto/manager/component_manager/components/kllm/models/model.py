"""
将 Model 作为一个对象, 可能分为多种 Model: ['llm', 'vlm', 'embedding', 'rerank', 'parser', 'audio']
"""

from ....base_component import BaseComponent
from .model_instance import ModelInstance


# TODO 要继承 BaseComponent
class Model(BaseComponent):
    OBJECT_TOKEN = "model_id"

    GET_URL_MAP = dict(
        aaa="/v1/kllm/models/types",
        bbb="/v1/kllm/models/{model_id}",
        get_instances="/v1/kllm/models/{model_id}/instances",
        ddd="/v1/kllm/models/user-pending-info",
        eee="/v1/kllm/models/access-statistic",
        get_models="/v1/kllm/models",
    )

    PUT_URL_MAP = dict(
        aaa="/v1/kllm/models/{model_id}",
    )

    POST_URL_MAP = dict(
        aaa="/v1/kllm/models",
        set_replicas="/v1/kllm/models/set_replicas",
    )

    DELETE_URL_MAP = dict(
        stop="/v1/kllm/models/{model_id}",
    )

    def stop(self, timeout=None):
        self.raw_delete("stop", timeout=timeout)

    @property
    def instances(self):
        res = self.raw_get("get_instances")
        return [
            ModelInstance(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip)
            for item in res.data.get("items")
        ]

    def set_replicas(self, replicas: int, timeout=None):
        data = {"id": self.object_id, "replicas": replicas}
        return self.raw_post("set_replicas", json=data, timeout=timeout)
