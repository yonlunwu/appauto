from time import time, sleep
from typing import Dict, TypeVar, Literal, TYPE_CHECKING, List

from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager.config_logging import LoggingConfig
from appauto.organizer.model_params.constructor import AMaaSModelParams

from appauto.manager.component_manager.components.amaas.models.model_store import (
    LLMModelStore,
    VLMModelStore,
    EmbeddingModelStore,
    RerankModelStore,
    AudioModelStore,
    ParserModelStore,
    BaseModelStore,
)

from appauto.manager.error_manager import ModelCheckError, ModelRunError

T = TypeVar("T", LLMModelStore, EmbeddingModelStore, VLMModelStore, RerankModelStore, ParserModelStore, AudioModelStore)

if TYPE_CHECKING:
    from .amaas_node import AMaaSNode

logger = LoggingConfig.get_logger()


class AMaaSNodeApi(AMaaS):
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
        node: "AMaaSNode" = None,
    ):
        super().__init__(mgt_ip, port, username, passwd, object_id, data, ssl_enabled, parent_tokens, amaas)
        self.node = node

    def model_store_check(self, model_store: T, params: Dict) -> Dict:
        res = model_store.check(**params)

        if res.data.messages:
            logger.error(f"error occurred while check model: {res.data.messages}")
            raise ModelCheckError(f"{model_store.name} check failed: {res.data.messages}, params: {params}")

        return res

    def model_store_run(self, model_store: T, params: Dict, timeout_s: int = 900):
        try:
            model_store.run(wait_for_running=True, running_timeout_s=timeout_s, **params)
        except Exception as e:
            logger.error(f"error occurred while running model: {str(e)}")
            raise ModelRunError(f"{model_store.name} check failed: {str(e)}, params: {params}")

    def launch_model_with_default(
        self, tp: Literal[1, 2, 4, 8], model_store: T, model_name: str = None, timeout_s: int = 900
    ):
        """
        从 yml 中读取默认参数, 发起检测 -> 拉起 -> 试验场景
        """
        params = AMaaSModelParams(self.node, model_store, tp, model_name).gen_default_params

        assert params, f"invalid params: {params}"

        self.model_store_check(model_store, params)
        self.model_store_run(model_store, params, timeout_s)

    def launch_model_with_perf(
        self, tp: Literal[1, 2, 4, 8], model_store: T, model_name: str = None, timeout_s: int = 900, max_total_tokens: int = None, num_gpu_experts: int = None
    ):
        """
        从 yml 中读取默认性能测试参数, 发起检测 -> 拉起 -> 性能测试场景
        """
        params = AMaaSModelParams(self.node, model_store, tp, model_name).gen_perf_params

        # 替换 max_total_tokens
        if max_total_tokens:
            params["max_total_tokens"] = max_total_tokens
        # 替换 num_gpu_experts
        if num_gpu_experts:
            # 查找并替换或添加参数
            backend_params = params["backend_parameters"]
            if "--num-gpu-experts" in backend_params:
                backend_params[backend_params.index("--num-gpu-experts") + 1] = str(num_gpu_experts)
            else:
                backend_params.extend(["--num-gpu-experts", str(num_gpu_experts)])
        logger.info(f"launch model with perf params: {params}")

        assert params, f"invalid params: {params}"

        self.model_store_check(model_store, params)
        self.model_store_run(model_store, params, timeout_s)

    def stop_model(self, model_store: T, type_: Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"]):

        if model_list := getattr(self.model, type_, None):
            if target_models := [
                m for m in model_list if m.display_model_name == model_store.name or m.name == model_store.name
            ]:
                for t_m in target_models:
                    t_m.stop()

    def wait_gpu_release(self, interval_s: int = 20, timeout_s: int = 180):
        start_time = time()

        while time() - start_time <= timeout_s:
            worker = self.workers[0]
            if worker.gpu_empty_count == worker.gpu_sum:
                return

            sleep(interval_s)

        raise TimeoutError(
            f"timeout while waiting for gpu released. total: {worker.gpu_sum}, empty: {worker.gpu_empty_count}"
        )

    def get_models_store(
        self,
        model_store_type: Literal["llm", "vlm", "embedding", "rerank", "parser", "audio"],
        priority: List[Literal["P0", "P1", "P2", "P3"]] = None,
    ) -> List[BaseModelStore]:

        model_stores = getattr(self.init_model_store, model_store_type)

        if priority:
            priority = priority if isinstance(priority, list) else [priority]
            return [m_s for m_s in model_stores if AMaaSModelParams(self.node, m_s, None).model_priority in priority]

        return model_stores
