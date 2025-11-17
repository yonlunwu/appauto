"""
测试 models 的默认参数检查 / 运行 / 试验场景 / 停止
"""

import pytest
import allure

from appauto.manager.config_manager import LoggingConfig
from appauto.manager.utils_manager import Requires

from testcases.amaas.gen_data import amaas, DefaultParams as DP
from testcases.amaas.api.conftest import (
    CommonModelBaseRunner as cr,
    DoCheck as dc,
)

logger = LoggingConfig.get_logger()


@allure.epic("TestAMaaSModelStoreBaseActionWithDefault")
class TestAMaaSModelStoreBaseActionWithDefault:
    @Requires.need_have(amaas.api, ["llm"])
    @pytest.mark.parametrize("model_store", cr.get_models_store("llm"))
    @pytest.mark.parametrize("tp", DP.tp)
    def test_init_llm_model_store_run_with_default_params(self, model_store, tp):
        """
        模型中心-llm: 默认参数检查 -> 运行 -> 试验场景
        """
        if model_store.name == "GLM-4.5-Air-GPU-weight" and int(tp) > 2:
            pytest.skip(f"skip due to {model_store.name} and tp {tp}")

        result = cr.run_with_default(tp, model_store)
        dc.check_final_item(result)

    @Requires.need_have(amaas.api, ["vlm"])
    @pytest.mark.parametrize("model_store", cr.get_models_store("vlm"))
    @pytest.mark.parametrize("tp", DP.tp)
    def test_init_vlm_model_store_run_with_default_params(self, model_store, tp):
        """
        模型中心-vlm: 默认参数检查 -> 运行 -> 试验场景
        """
        if model_store.name != "GLM-4.5V-GPU-weight" and tp in [4, 8]:
            pytest.skip(f"skip due to {model_store.name}, tp: {tp}")

        result = cr.run_with_default(tp, model_store)
        dc.check_final_item(result)

    @Requires.need_have(amaas.api, ["embedding"])
    @pytest.mark.parametrize("model_store", cr.get_models_store("embedding"))
    # TODO embedding 应该也只允许 1 卡？
    @pytest.mark.parametrize("tp", [1])
    def test_init_embedding_model_store_run_with_default_params(self, model_store, tp):
        """
        模型中心-embedding: 默认参数检查 -> 运行 -> 试验场景
        """
        result = cr.run_with_default(tp, model_store)
        dc.check_final_item(result)

    @Requires.need_have(amaas.api, ["rerank"])
    @pytest.mark.parametrize("model_store", cr.get_models_store("rerank"))
    # TODO rerank 应该也只允许 1 卡？
    @pytest.mark.parametrize("tp", [1])
    def test_init_rerank_model_store_run_with_default_params(self, model_store, tp):
        """
        模型中心-rerank: 默认参数检查 -> 运行 -> 试验场景
        """
        result = cr.run_with_default(tp, model_store)
        dc.check_final_item(result)

    @Requires.need_have(amaas.api, ["parser"])
    @pytest.mark.parametrize("model_store", cr.get_models_store("parser"))
    @pytest.mark.parametrize("tp", [1])
    def test_init_parser_model_store_run_with_default_params(self, model_store, tp):
        """
        模型中心-parser: 默认参数检查 -> 运行 -> 试验场景
        """
        result = cr.run_with_default(tp, model_store)
        dc.check_final_item(result)

    @Requires.need_have(amaas.api, ["audio"])
    @pytest.mark.parametrize("model_store", cr.get_models_store("audio"))
    @pytest.mark.parametrize("tp", [1])
    def test_init_audio_model_store_run_with_default_params(self, model_store, tp):
        """
        模型中心-audio: 默认参数检查 -> 运行 -> 试验场景
        """
        result = cr.run_with_default(tp, model_store)
        dc.check_final_item(result)
