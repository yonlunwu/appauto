from typing import List, Dict, TYPE_CHECKING
from .....utils_manager.custom_list import CustomList
from ....base_component import BaseComponent
from .gpu import GPU


if TYPE_CHECKING:
    from .model_instance import ModelInstance


class Worker(BaseComponent):
    OBJECT_TOKEN = "gpu_device_id"

    GET_URL_MAP = dict(
        get_resource_list="/v1/kllm/workers/get_resource_list",
    )

    def __str__(self):
        return f"Worker(Name: {self.name}, ID: {self.object_id})"

    def get_resource_list(self, timeout=None):
        return self.get("get_resource_list", timeout=timeout)

    @property
    def gpus(self, timeout=None) -> CustomList[GPU]:
        data = {"worker_id": str(self.object_id)}
        res = self.post("detail", json_data=data, url_map=GPU.POST_URL_MAP, timeout=timeout)
        return CustomList(
            [
                GPU(self.mgt_ip, self.port, object_id=inner_dict.gpu_id, data=inner_dict, idx=idx, worker=self)
                for idx, inner_dict in res.data.get(self.name).items()
            ]
        )

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

    @property
    def model_instances_obj(self) -> CustomList["ModelInstance"]:
        if models := self.amaas.models:
            if instances := self.model_instances:
                return CustomList(
                    [
                        ins
                        for model in models
                        for ins in model.instances
                        if ins.name in [item.name for item in instances]
                    ]
                )
