import abc
from typing import Literal
from ...base_component import BaseComponent


class BaseScene(BaseComponent):
    OBJECT_TOKEN = "scene_chat_id"

    GET_URL_MAP = dict(get_self="/v1/models")

    POST_URL_MAP = dict(
        llm_vlm="/v1/chat/completions",  # llm & vlm
        embedding="/v1/embeddings",  # embedding
        embedding_compute_similarity="/v1/kllm/embedding/compute_similarity",  # embedding
        rerank="/v1/rerank",  # rerank
    )

    @property
    def created(self):
        return self.data.created

    @property
    def display_model_name(self):
        return self.data.display_model_name

    @property
    def object(self) -> Literal["model"]:
        return self.data.object

    @property
    def owned_by(self) -> Literal["AMES"]:
        return self.data.owned_by

    @property
    def meta(self) -> Literal[None]:
        return self.data.meta

    @abc.abstractmethod
    def chat(self): ...
