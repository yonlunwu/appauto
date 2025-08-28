"""
将 Model 作为一个对象, 可能分为多种 Model: ['llm', 'vlm', 'embedding', 'rerank', 'parser', 'audio']
"""

import json
from typing import Literal, Dict, List
from copy import deepcopy
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
        create_replica="/v1/kllm/models/create-replica",
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

    def check(
        self,
        worker_id: int = None,
        gpu_ids: List = None,
        tp: Literal[1, 2, 4, 8] = 1,
        hicache: int = 0,
        timeout=None,
    ):
        from .model_store import ModelStore

        assert tp or gpu_ids
        assert isinstance(hicache, int)

        b_p_list = deepcopy(self.backend_parameters)
        b_p_dict = {b_p_list[i]: b_p_list[i + 1] for i in range(0, len(b_p_list), 2)}

        b_p_dict["--tensor-parallel-size"] = "0" if gpu_ids else str(tp)

        data = {
            "id": [m_s.object_id for m_s in self.amaas.init_model_stores if m_s.name == self.name][0],
            "worker_id": str(worker_id),
            "gpu_ids": gpu_ids,
            "access_limit": self.access_limit,
            "backend_parameters": [item for k, v in b_p_dict.items() for item in (k, v)],
            "fixed_backend_parameters": [],  # fixed 在这里表示高级参数，v3.3.0 这个版本固定为 []
            "replicas": 1,  # v3.3.0 版本只能添加 1 个副本
            "cache_storage": hicache,
        }

        self.post("check", json_data=data, url_map=ModelStore.POST_URL_MAP, timeout=timeout)

    def create_replica(
        self, worker_id: int, tp: Literal[1, 2, 4, 8] = 1, gpu_ids: List = None, hicache: int = 0, timeout=None
    ) -> ModelInstance:
        assert tp or gpu_ids
        assert isinstance(hicache, int)

        # 先获取所有副本
        before = self.instances

        b_p_list = deepcopy(self.backend_parameters)
        b_p_dict = {b_p_list[i]: b_p_list[i + 1] for i in range(0, len(b_p_list), 2)}

        b_p_dict["--tensor-parallel-size"] = "0" if gpu_ids else str(tp)

        data = {
            "model_id": self.object_id,
            "worker_id": str(worker_id),
            "gpu_ids": gpu_ids,
            "access_limit": self.access_limit,
            "backend_parameters": [item for k, v in b_p_dict.items() for item in (k, v)],
            "fixed_backend_parameters": [],  # fixed 在这里表示高级参数，v3.3.0 这个版本固定为 []
            "replicas": 1,  # v3.3.0 版本只能添加 1 个副本
            "cache_storage": hicache,
        }

        self.post("create_replica", json_data=data, timeout=timeout)

        # 再次获取所有副本
        return [ins for ins in self.instances if ins not in before][0]

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
