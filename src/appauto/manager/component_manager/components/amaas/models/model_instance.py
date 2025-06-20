from ....base_component import BaseComponent


# TODO 要继承 BaseComponent
class ModelInstance(BaseComponent):
    OBJECT_TOKEN = "model_instance_id"

    GET_URL_MAP = dict(
        get_instances="/v1/kllm/model-instances",
        get_info="/v1/kllm/model-instances/{model_instance_id}",
        get_logs="/v1/kllm/model-instances/{model_instance_id}/logs",
    )

    PUT_URL_MAP = dict(
        aaa="/v1/kllm/models/{model_instance_id}",
    )

    POST_URL_MAP = dict(
        aaa="/v1/kllm/models",
        bbb="/v1/kllm/models/set_replicas",
    )

    DELETE_URL_MAP = dict(
        stop="/v1/kllm/model-instances/{model_instance_id}",
    )

    # TODO BUG rc=500
    def get_logs(self, timeout=None):
        return self.get("get_logs", timeout=timeout)

    def get_info(self, timeout=None):
        return self.get("get_info", timeout=timeout)

    # TODO 这是在做什么事情？
    def delete(self, timeout=None):
        return self.delete("stop", timeout=timeout)
