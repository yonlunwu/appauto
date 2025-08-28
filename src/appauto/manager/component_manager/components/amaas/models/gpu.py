from typing import List, Dict, Literal, TYPE_CHECKING, Optional
from ....base_component import BaseComponent
from .....utils_manager.custom_list import CustomList


if TYPE_CHECKING:
    from .worker import Worker
    from .model_instance import ModelInstance


class GPU(BaseComponent):

    OBJECT_TOKEN = "gpu_device_id"

    GET_URL_MAP = dict(
        get_resource_list="/v1/kllm/workers/get_resource_list",
    )

    POST_URL_MAP = dict(
        detail="/v1/kllm/gpu-devices/detail",
    )

    def __init__(
        self,
        mgt_ip=None,
        port=None,
        username="admin",
        passwd="123456",
        object_id=None,
        data=None,
        ssl_enabled=False,
        parent_tokens=None,
        amaas=None,
        idx=None,
        worker: "Worker" = None,
    ):
        super().__init__(mgt_ip, port, username, passwd, object_id, data, ssl_enabled, parent_tokens, amaas)
        self.idx = idx
        self.worker = worker

    def __str__(self):
        return f"GPU(Name: {self.name}, ID: {self.object_id}, worker: {self.worker.name},)"

    @property
    def name(self):
        return self.data.name

    @property
    def uuid(self):
        return self.data.uuid

    @property
    def vendor(self) -> Literal["NVIDIA"]:
        return self.data.vendor

    @property
    def index(self) -> int:
        return self.data.index

    @property
    def core(self) -> Dict:
        return self.data.core

    @property
    def memory(self) -> Dict:
        return self.data.memory

    @property
    def temperature(self) -> float:
        return self.data.temperature

    @property
    def labels(self) -> Dict:
        return self.data.labels

    @property
    def type(self) -> Literal["cuda"]:
        return self.data.type

    @property
    def worker_id(self):
        """当前 data 中是空的"""
        return self.data.worker_id

    @property
    def worker_name(self):
        """当前 data 中是空的"""
        return self.data.worker_name

    @property
    def worker_ip(self):
        """当前 data 中是空的"""
        return self.data.worker_ip

    # TODO 是否要直接获取 instance_obj, 而不是 instance_dict
    @property
    def model_instances(self) -> Optional[List[Dict]]:
        return self.data.model_instances

    @property
    def model_instances_obj(self) -> CustomList["ModelInstance"]:
        if ins_dict := self.model_instances:
            if ins_obj := self.worker.model_instances_obj:
                return CustomList([ins for ins in ins_obj if ins.name in [item.name for item in ins_dict]])

    @property
    def gpu_id(self) -> str:
        return self.data.gpu_id
