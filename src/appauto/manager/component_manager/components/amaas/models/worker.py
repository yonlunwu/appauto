from typing import List, Dict
from ....base_component import BaseComponent


class Worker(BaseComponent):
    OBJECT_TOKEN = "gpu_device_id"

    GET_URL_MAP = dict(
        get_resource_list="/v1/kllm/workers/get_resource_list",
    )

    POST_URL_MAP = dict(
        list_gpu_device="/v1/kllm/gpu-devices/detail",
    )

    def get_resource_list(self, timeout=None):
        return self.get("get_resource_list", timeout=timeout)

    @property
    def gpu_sum(self) -> int:
        return self.data.gpu_sum

    @property
    def gpu_empty_count(self) -> int:
        return self.data.gpu_empty_count

    @property
    def gpu_total_vram(self) -> int:
        return self.data.gpu_total_vram

    @property
    def gpu_empty_vram(self) -> int:
        return self.data.gpu_empty_vram

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def cache_capacity(self) -> int:
        return self.data.cache_capacity

    @property
    def cache_total(self) -> int:
        return self.data.cache_total

    @property
    def cache_available(self) -> int:
        return self.data.cache_available

    @property
    def cache_used(self) -> int:
        return self.data.cache_used

    @property
    def model_instances(self) -> List[Dict]:
        return self.data.model_instances
