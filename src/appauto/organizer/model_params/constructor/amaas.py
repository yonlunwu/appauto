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
from ....manager.error_manager.errors import OperationNotSupported
from .base_model_config import BaseModelConfig


if TYPE_CHECKING:
    from ....operator.amaas_node import AMaaSNode

logger = LoggingConfig.get_logger()

T = TypeVar("T", LLMModelStore, EmbeddingModelStore, VLMModelStore, RerankModelStore, ParserModelStore, AudioModelStore)


class AMaaSModelParams(BaseModelConfig):
    def __init__(self, amaas: "AMaaSNode", model_store: T, tp: int, model_name: str = None):
        """
        model_name 默认是 model_store.name, 但存在某些情况 model_store.name 与 model_name 并不一致.
        """
        self.amaas = amaas
        self.model_store = model_store
        self.tp = tp
        self.model_name = model_name or model_store.name

    @cached_property
    def handler(self) -> YMLHandler:
        yml_path = f"src/appauto/organizer/model_params/{self.amaas.cli.gpu_type}/{self.model_type}/"
        yml_path += f"{self.model_family}/{self.model_name}.yaml" if self.model_family else f"{self.model_name}.yaml"

        return YMLHandler(yml_path)

    def __gen_params_from_rule(self) -> ADDict:
        """
        获取 model_store 中对应模型的默认参数
        """
        rule: ADDict = self.model_store.get_run_rule()

        worker = choice(self.amaas.api.workers)

        params = ADDict(
            worker_id=worker.object_id,
            tp=self.tp,
            access_limit=rule.data.access_limit,
        )

        match self.model_store:
            case LLMModelStore() | VLMModelStore() | EmbeddingModelStore() | RerankModelStore():
                params.max_total_tokens = rule.data.max_total_tokens

        return params

    @cached_property
    def gen_default_params(self) -> ADDict:
        # Dict
        # 如果不存在 amaas 需要 raise 出一个不支持的错误.
        if yml_data := self.handler.data.amaas.correct:

            # 存在指定的 tp 说明支持该 tp, 否则说明是不支持的
            # 如果支持该 tp 则按需生成 params

            params = ADDict()

            if spt_tp_params := yml_data.get(self.tp, False):
                # spt_tp_params 可能会有 2 种情况, default 或非 default(此时通常是 dict)
                # default 表示直接从 get_run_rule 中获取默认参数
                # 非 default 表示 yaml 中该 tp 的配置需要与 get_run_rule 的结果做组合

                params = self.__gen_params_from_rule()
                if spt_tp_params != "default":
                    params.update(spt_tp_params)

                logger.info(f"params: {params}")

                return params

            raise OperationNotSupported(f"{self.model_name} doesn't support tp {self.tp}.")

        raise OperationNotSupported(f"{self.model_name} doesn't support tp {self.tp}.")

    @cached_property
    def gen_perf_params(self) -> ADDict:
        """
        规则: amaas 以性能测试拉起模型, 实际一般修改 cpu-infer 和其他高级参数(backend_parameters)
        """
        if perf := self.handler.data.amaas.perf:
            params = ADDict()

            # perf_common 的修改一般包含 backend_params 和 max-total-tokens（fixed_backend_params 中）
            perf_common = self.handler.data.amaas.perf_common or {}
            b_p_from_p_c = [item for k, v in perf_common.backend_parameters.items() for item in (f"--{k}", f"{v}")]
            # TODO kt-cpuinfer
            b_p_from_p_c.extend(["--kt-cpuinfer", "90" if self.amaas.cli.cpuinfer == 96 else "60"])

            if spt_tp_params := perf.get(self.tp, False):
                # spt_tp_params 可能会有 2 种情况, default 或非 default(此时通常是 dict)
                # default 表示直接从 get_run_rule 中获取默认参数
                # 非 default 表示 yaml 中该 tp 的配置需要与 get_run_rule 的结果做组合(通常是修改 backend_parameters)

                params = self.__gen_params_from_rule()
                if spt_tp_params != "default":
                    # 修改 backend_parameters
                    if isinstance(spt_tp_params, dict) and "backend_parameters" in spt_tp_params:
                        tmp = {}
                        res = [
                            item
                            for d in spt_tp_params["backend_parameters"]
                            for k, v in d.items()
                            for item in (f"--{k}", f"{v}")
                        ]
                        b_p_from_p_c.extend(res)
                        tmp["backend_parameters"] = b_p_from_p_c
                        params.update(tmp)

                    # 修改 fixed_backend_parameters 中的 max_total_tokens
                    if max_total_tokens := perf_common.max_total_tokens:
                        params.update(dict(max_total_tokens=max_total_tokens))

                logger.info(f"perf params: {params}")

                return params

            raise OperationNotSupported(f"{self.model_name} doesn't support tp {self.tp} for perf.")

        raise OperationNotSupported(f"{self.model_name} doesn't support tp {self.tp} for perf.")
