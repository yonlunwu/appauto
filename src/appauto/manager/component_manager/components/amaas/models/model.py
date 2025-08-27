"""
将 Model 作为一个对象, 可能分为多种 Model: ['llm', 'vlm', 'embedding', 'rerank', 'parser', 'audio']
"""

from typing import Literal, Dict, List
from ....base_component import BaseComponent
from .model_instance import ModelInstance
from .....utils_manager.custom_list import CustomList


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
        self.delete("stop", timeout=timeout)

    # TODO CustomList
    @property
    def instances(self) -> CustomList[ModelInstance]:
        """模型实例"""
        res = self.get("get_instances")
        return CustomList(
            [
                ModelInstance(port=self.port, data=item, object_id=item.id, mgt_ip=self.mgt_ip)
                for item in res.data.get("items")
            ]
        )

    def set_replicas(self, replicas: int, timeout=None):
        data = {"id": self.object_id, "replicas": replicas}
        return self.post("set_replicas", json_data=data, timeout=timeout)

    @property
    def name(self):
        return self.data.name

    @property
    def description(self):
        return self.data.description

    @property
    def source(self) -> Literal["local_path"]:
        return self.data.source

    @property
    def replicas(self) -> int:
        return self.data.replicas

    @property
    def ready_replicas(self) -> int:
        return self.data.ready_replicas

    @property
    def huggingface_repo_id(self):
        return self.data.huggingface_repo_id

    @property
    def huggingface_filename(self):
        return self.data.huggingface_filename

    @property
    def ollama_library_model_name(self):
        return self.data.ollama_library_model_name

    @property
    def model_scope_model_id(self):
        return self.data.model_scope_model_id

    @property
    def model_scope_file_path(self):
        return self.data.model_scope_file_path

    @property
    def local_path(self):
        return self.data.local_path

    @property
    def model_store_id(self) -> int:
        return self.data.model_store_id

    @property
    def categories(self) -> List:
        return self.data.categories

    @property
    def placement_strategy(self):
        return self.data.placement_strategy

    @property
    def cpu_offloading(self) -> bool:
        return self.data.cpu_offloading

    @property
    def distributed_inference_across_workers(self) -> bool:
        return self.data.distributed_inference_across_workers

    @property
    def worker_selector(self) -> Dict:
        return self.data.worker_selector

    @property
    def gpu_selector(self):
        return self.data.gpu_selector

    @property
    def worker_id_selector(self) -> str:
        return self.data.worker_id_selector

    @property
    def vram_count(self) -> int:
        return self.data.vram_count

    @property
    def gpu_count(self) -> int:
        return self.data.gpu_count

    @property
    def token_count(self) -> int:
        return self.data.token_count

    @property
    def access_limit(self) -> int:
        return self.data.access_limit

    @property
    def status(self) -> Literal["running", "loading", "error"]:
        return self.data.status

    @property
    def family(self) -> Literal["DeepSeek", "Qwen", "parser", "BGE"]:
        return self.data.family

    @property
    def meta(self) -> Dict:
        return self.data.meta

    @property
    def backend_version(self) -> Literal["ftransformers", "llama-box", "pdf_parse_server"]:
        return self.data.backend_version

    @property
    def backend_parameters(self):
        return self.data.backend_parameters

    @property
    def backend_version(self):
        return self.data.backend_version

    @property
    def backend_parameters(self) -> List:
        return self.data.backend_parameters

    @property
    def embedding_only(self) -> bool:
        return self.data.embedding_only

    @property
    def image_only(self) -> bool:
        return self.data.image_only

    @property
    def reranker(self) -> bool:
        return self.data.reranker

    @property
    def speech_to_text(self) -> bool:
        return self.data.speech_to_text

    @property
    def text_to_speech(self) -> bool:
        return self.data.text_to_speech

    @property
    def placement_strategy(self) -> Literal["spread"]:
        return self.data.placement_strategy

    @property
    def cache_storage(self) -> int:
        return self.data.cache_storage

    @property
    def max_total_tokens(self) -> int:
        return self.data.max_total_tokens

    @property
    def created_at(self) -> str:
        return self.data.created_at

    @property
    def updated_at(self) -> str:
        return self.data.updated_at

    @property
    def display_model_name(self) -> str:
        return self.data.display_model_name
