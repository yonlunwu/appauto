"""
Module for constructing model parameters for amaas.
"""

from random import choice
from addict import Dict as ADDict
from typing import Literal, TypeVar, Dict, TYPE_CHECKING
from functools import cached_property
from ....manager.file_manager.handle_yml import YMLHandler
from ....manager.config_manager.config_logging import LoggingConfig
from ....manager.component_manager.components.amaas.models.model_store import (
    LLMModelStore,
    VLMModelStore,
    EmbeddingModelStore,
    RerankModelStore,
    AudioModelStore,
    ParserModelStore,
)

if TYPE_CHECKING:
    from ....operator.amaas_node import AMaaSNodeApi

logger = LoggingConfig.get_logger()

T = TypeVar("T", LLMModelStore, EmbeddingModelStore, VLMModelStore, RerankModelStore, ParserModelStore, AudioModelStore)


class AMaaSModelParams:
    def __init__(self, amaas: "AMaaSNodeApi", model_store: T, tp: int, model_name: str = None):
        """
        model_name 默认是 model_store.name, 但存在某些情况 model_store.name 与 model_name 并不一致.
        """
        self.amaas = amaas
        self.model_store = model_store
        self.tp = tp
        self.model_name = model_name or model_store.name

    @cached_property
    def gpu_type(self) -> str:
        # TODO 根据 self.node 获取实际 GPU 类型
        return "nvidia"

    @cached_property
    def model_type(self) -> str:
        # TODO 根据 self.model_name 获取实际模型类型
        return "llm"

    @cached_property
    def model_family(self) -> Literal["deepseek", "qwen", "glm", "kimi"]:
        if self.model_name.startswith("DeepSeek"):
            return "deepseek"
        elif self.model_name.startswith("GLM"):
            return "glm"
        elif self.model_name.startswith("Qwen"):
            return "qwen"
        elif self.model_name.startswith("Kimi"):
            return "kimi"

    @cached_property
    def handler(self) -> YMLHandler:
        # 根据 model_name, tp, mode 返回对应的 yaml 路径
        # TODO 1. 根据 self.node 获取卡类型
        yml_path = f"src/appauto/organizer/model_params/{self.gpu_type}/{self.model_type}/{self.model_family}/{self.model_name}.yaml"
        return YMLHandler(yml_path)

    def __gen_params_from_rule(self, tp: int) -> ADDict:
        """
        获取 model_store 中对应模型的默认参数
        """
        rule: ADDict = self.model_store.get_run_rule()

        worker = choice(self.amaas.workers)

        params = ADDict(
            worker_id=worker.object_id,
            tp=tp,
            access_limit=rule.data.access_limit,
        )

        match self.model_store:
            case LLMModelStore() | VLMModelStore() | EmbeddingModelStore() | RerankModelStore():
                params.max_total_tokens = rule.data.max_total_tokens

        return params

    @cached_property
    def gen_params(self) -> ADDict:
        # Dict
        yml_data = self.handler.data.amaas

        # 存在指定的 tp 说明支持该 tp, 否则说明是不支持的
        # 如果支持该 tp 则进行 cmd 合并拼接

        params = ADDict()

        if spt_tp_params := yml_data.get(self.tp, False):
            # spt_tp_params 可能会有 2 种情况, default 或非 default(此时通常是 dict)
            # default 表示直接从 get_run_rule 中获取默认参数
            # 非 default 表示 yaml 中该 tp 的配置需要与 get_run_rule 的结果做组合

            params = self.__gen_params_from_rule(self.tp)
            if spt_tp_params != "default":
                params.update(spt_tp_params)

        logger.info(f"params: {params}")

        return params
