from typing import List, Dict, TYPE_CHECKING, Optional
from functools import cached_property
from ....base_component import BaseComponent
from .....utils_manager.custom_list import CustomList

if TYPE_CHECKING:
    from .model import Model
    from .worker import Worker
    from .gpu import GPU


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
    )

    DELETE_URL_MAP = dict(
        stop="/v1/kllm/model-instances/{model_instance_id}",
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
        model: "Model" = None,
    ):
        super().__init__(mgt_ip, port, username, passwd, object_id, data, ssl_enabled, parent_tokens, amaas)
        self.model = model

    def __str__(self):
        return f"ModelInstance(Name:{self.name}, ID:{self.object_id})"

    def __contains__(self, items: List["ModelInstance"]):
        return self.object_id in [item.object_id for item in items]

    # TODO 要感知所在的 gpu 和 worker
    @cached_property
    def worker(self) -> Optional["Worker"]:
        if workers := self.model.amaas.workers:
            return [worker for worker in workers if self.worker_name == worker.name][0]

    @cached_property
    def gpus(self) -> CustomList["GPU"]:
        return CustomList(
            [gpu for gpu in self.worker.gpus if int(gpu.index) in [int(g_i.split(":")[-1]) for g_i in self.gpu_indexes]]
        )

    # TODO BUG rc=500
    def get_logs(self, timeout=None):
        return self.get("get_logs", timeout=timeout)

    def get_info(self, timeout=None):
        return self.get("get_info", timeout=timeout)

    def stop(self, timeout=None):
        return self.delete("stop", timeout=timeout)

    @property
    def local_path(self) -> str:
        return self.data.local_path

    # TODO Literal
    @property
    def state(self) -> str:
        return self.data.state

    @property
    def source(self) -> str:
        return self.data.source

    @property
    def huggingface_repo_id(self):
        return self.data.huggingface_repo_id

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def state_message(self):
        return self.data.state_message

    @property
    def worker_ip(self) -> str:
        return self.data.worker_ip

    @property
    def worker_id(self) -> int:
        return self.data.worker_id

    @property
    def worker_name(self) -> str:
        return self.data.worker_name

    @property
    def pid(self) -> int:
        return self.data.pid

    @property
    def distributed_servers(self) -> Dict:
        return self.data.distributed_servers

    @property
    def model_id(self) -> int:
        return self.data.model_id

    @property
    def model_name(self) -> str:
        return self.data.model_name

    @property
    def huggingface_filename(self) -> str:
        return self.data.huggingface_filename

    @property
    def ollama_library_model_name(self) -> str:
        return self.data.ollama_library_model_name

    @property
    def computed_resource_claim(self) -> Dict:
        return self.data.computed_resource_claim

    @property
    def cache_storage(self) -> int:
        return self.data.cache_storage

    @property
    def model_scope_model_id(self) -> str:
        return self.data.model_scope_model_id

    @property
    def model_scope_file_path(self) -> str:
        return self.data.model_scope_file_path

    @property
    def instance_port(self) -> int:
        return self.data.port

    @property
    def max_total_tokens(self) -> int:
        return self.data.max_total_tokens

    @property
    def deleted_at(self) -> str:
        return self.data.deleted_at

    @property
    def download_progress(self) -> float:
        return self.data.download_progress

    @property
    def backend_parameters(self) -> List:
        return self.data.backend_parameters

    @property
    def launch_parameters(self) -> List:
        return self.data.launch_parameters

    @property
    def gpu_indexes(self) -> List[str]:
        return self.data.gpu_indexes
