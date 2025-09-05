from typing import List, Dict, TYPE_CHECKING
from .....utils_manager.custom_list import CustomList
from ..base_component import BaseComponent
from .gpu import GPU


if TYPE_CHECKING:
    from .model_instance import ModelInstance


class Worker(BaseComponent):
    OBJECT_TOKEN = "worker_id"

    GET_URL_MAP = dict(
        get_self="/v1/kllm/workers/get_resource_list",
    )

    def __str__(self):
        return f"Worker(Name: {self.name}, ID: {self.object_id})"

    def refresh(self, alias=None):
        res = super().refresh(alias)
        self.data = [item for item in res.data.worker_resource_list if item.id == self.object_id][0]
        return res

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
    def llm_instances_obj(self) -> CustomList["ModelInstance"]:
        if llm_models := self.amaas.model.llm:
            if llm_instances := [ins for llm in llm_models for ins in llm.instances]:
                return CustomList(
                    [ins for ins in llm_instances if ins.name in [item.name for item in self.model_instances]]
                )

    @property
    def embedding_instances_obj(self) -> CustomList["ModelInstance"]:
        if embedding_models := self.amaas.model.embedding:
            if embedding_instances := [ins for embedding in embedding_models for ins in embedding.instances]:
                return CustomList(
                    [ins for ins in embedding_instances if ins.name in [item.name for item in self.model_instances]]
                )

    @property
    def rerank_instances_obj(self) -> CustomList["ModelInstance"]:
        if rerank_models := self.amaas.model.rerank:
            if rerank_instances := [ins for rerank in rerank_models for ins in rerank.instances]:
                return CustomList(
                    [ins for ins in rerank_instances if ins.name in [item.name for item in self.model_instances]]
                )

    @property
    def parser_instances_obj(self) -> CustomList["ModelInstance"]:
        if parser_models := self.amaas.model.parser:
            if parser_instances := [ins for parser in parser_models for ins in parser.instances]:
                return CustomList(
                    [ins for ins in parser_instances if ins.name in [item.name for item in self.model_instances]]
                )

    @property
    def vlm_instances_obj(self) -> CustomList["ModelInstance"]:
        if vlm_models := self.amaas.model.vlm:
            if vlm_instances := [ins for vlm in vlm_models for ins in vlm.instances]:
                return CustomList(
                    [ins for ins in vlm_instances if ins.name in [item.name for item in self.model_instances]]
                )

    @property
    def audio_instances_obj(self) -> CustomList["ModelInstance"]:
        if audio_models := self.amaas.model.audio:
            if audio_instances := [ins for audio in audio_models for ins in audio.instances]:
                return CustomList(
                    [ins for ins in audio_instances if ins.name in [item.name for item in self.model_instances]]
                )
