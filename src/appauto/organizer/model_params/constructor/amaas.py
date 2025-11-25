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
        try:
            # 存在 perf 说明 yml 支持 perf 模式, 否则不支持
            data = self.handler.data.amaas
            assert data.perf_common
            assert data.perf

            params = self.__gen_params_from_rule()

            # perf_common 中有可能存在 max_total_tokens
            if max_total_tokens := data.perf_common.max_total_tokens:
                params.max_total_tokens = max_total_tokens

            # 预期 perf_common 一定存在 backend_parameters：要关闭 cache
            b_p = [item for k, v in data.perf_common.backend_parameters.items() for item in (f"--{k}", f"{v}")]
            # backend_params 中要修改 cpuinfer
            b_p.extend(["--kt-cpuinfer", "90" if self.amaas.cli.cpuinfer == 96 else "60"])
            params.backend_parameters = b_p

            # 存在 tp 说明支持该 tp 的 perf 模式，否则不支持
            # spt_tp_params 取值：default 或非 default(此时通常是 dict)
            # default：直接从 get_run_rule 中获取默认参数，但依然需要结合 perf_common
            # 非 default：从 yaml 中读出指定 tp，并与 get_run_rule 结果和 perf_common 做组合(通常是修改 backend_parameters)
            # 因此无论什么情况都需要先 get_run_rule 和 获取 perf_common
            tp_data = data.perf.get(self.tp, None)
            assert tp_data

            # 当 tp 不是 default 时, 还需要结合 get_run_rule 进一步修改 backend_parameters
            if tp_data != "default":

                assert isinstance(tp_data, dict)

                if "backend_parameters" in tp_data:
                    fmt = [item for k, v in tp_data["backend_parameters"].items() for item in (f"--{k}", f"{v}")]
                    params.backend_parameters.extend(fmt)

                # tp 中如果指定了 max_total_tokens 需要覆盖 perf_common 中的值
                if "max_total_tokens" in tp_data:
                    params.max_total_tokens = tp_data.max_total_tokens

            logger.info(f"perf params: {params}")

            return params

        except AssertionError:
            raise OperationNotSupported(f"{self.model_name} doesn't support tp {self.tp} for perf.")
