from addict import Dict as ADDict
from functools import cached_property
from functools import cached_property
from typing import Literal, TypeVar, Optional
from ....manager.file_manager.handle_yml import YMLHandler
from ....manager.component_manager.components.amaas.models.model_store import (
    LLMModelStore,
    VLMModelStore,
    EmbeddingModelStore,
    RerankModelStore,
    AudioModelStore,
    ParserModelStore,
)


T = TypeVar("T", LLMModelStore, EmbeddingModelStore, VLMModelStore, RerankModelStore, ParserModelStore, AudioModelStore)


class BaseModelConfig:
    YML_PATH = "src/appauto/organizer/model_params/model_config.yaml"

    @cached_property
    def model_config(self) -> ADDict:
        return YMLHandler(self.YML_PATH).data

    @cached_property
    def model_type(self) -> Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"]:
        return self.model_config.get(self.model_name, ADDict()).type or "llm"

    @cached_property
    def model_priority(self) -> Literal["P0", "P1", "P2", "P3"]:
        return self.model_config.get(self.model_name, ADDict()).priority or "P0"

    @cached_property
    def model_family(self) -> Optional[Literal["deepseek", "qwen", "glm", "kimi"]]:
        if self.model_name.startswith("DeepSeek"):
            return "deepseek"
        elif self.model_name.startswith("GLM"):
            return "glm"
        elif self.model_name.startswith("Qwen"):
            return "qwen"
        elif self.model_name.startswith("Kimi"):
            return "kimi"
