"""
基于 amaas 执行 sanity_check.
"""

import allure
import pytest

from appauto.manager.config_manager import LoggingConfig
from appauto.manager.utils_manager import Requires


from testcases.sanity_check.amaas.gen_data import amaas, DefaultParams as DP
from testcases.sanity_check.amaas.conftest import CommonModelBaseStep as cs


logger = LoggingConfig.get_logger()


@allure.epic("Test_Sanity_Check_AMaaS_Base_Action_With_Default")
@pytest.mark.amaas_ci_sanity_check
class Test_Sanity_Check_AMaaS_Base_Action_With_Default:
    @Requires.need_have(amaas.api, ["llm"])
    @pytest.mark.parametrize("model_store", amaas.api.get_models_store("llm", DP.model_priority))
    @pytest.mark.parametrize("tp", DP.tp)
    def test_sanity_check_init_llm_model_store_run_with_default_params(self, tp, model_store, worker_gpu_count):
        """
        模型中心-llm: 默认参数检查 -> 运行 -> 试验场景
        """
        if worker_gpu_count < tp:
            pytest.skip(f"insufficent gpu count: {worker_gpu_count} < {tp}")

        try:
            cs.launch_model(model_store, tp)
            cs.scene_and_stop(model_store, skip_scene=False)

        except Exception as e:
            logger.error(f"error occurred while testing llm: {e}")
            pytest.fail(f"error occurred while testing llm: {e}")

        finally:
            cs.stop(model_store, "llm")

    @Requires.need_have(amaas.api, ["vlm"])
    @pytest.mark.parametrize("model_store", amaas.api.get_models_store("vlm", DP.model_priority))
    @pytest.mark.parametrize("tp", DP.tp)
    def test_sanity_check_init_vlm_model_store_run_with_default_params(self, tp, model_store, worker_gpu_count):
        """
        模型中心-vlm: 默认参数检查 -> 运行 -> 试验场景
        """
        if worker_gpu_count < tp:
            pytest.skip(f"insufficent gpu count: {worker_gpu_count} < {tp}")

        try:
            cs.launch_model(model_store, tp)
            cs.scene_and_stop(model_store, skip_scene=False)

        except Exception as e:
            logger.error(f"error occurred while testing vlm: {e}")
            pytest.fail(f"error occurred while testing vlm: {e}")

        finally:
            cs.stop(model_store, "vlm")

    @Requires.need_have(amaas.api, ["embedding"])
    @pytest.mark.parametrize("model_store", amaas.api.get_models_store("embedding", DP.model_priority))
    def test_init_embedding_model_store_run_with_default_params(self, model_store):
        """
        模型中心-embedding: 默认参数检查 -> 运行 -> 试验场景, 只测试 1 卡.
        """

        try:
            cs.launch_model(model_store, 1)
            cs.scene_and_stop(model_store, skip_scene=False)

        except Exception as e:
            logger.error(f"error occurred while testing embedding: {e}")
            pytest.fail(f"error occurred while testing embedding: {e}")

        finally:
            cs.stop(model_store, "embedding")

    @Requires.need_have(amaas.api, ["rerank"])
    @pytest.mark.parametrize("model_store", amaas.api.get_models_store("rerank", DP.model_priority))
    def test_init_rerank_model_store_run_with_default_params(self, model_store):
        """
        模型中心-rerank: 默认参数检查 -> 运行 -> 试验场景, 只测试 1 卡.
        """

        try:
            cs.launch_model(model_store, 1)
            cs.scene_and_stop(model_store, skip_scene=False)

        except Exception as e:
            logger.error(f"error occurred while testing rerank: {e}")
            pytest.fail(f"error occurred while testing rerank: {e}")

        finally:
            cs.stop(model_store, "rerank")

    @Requires.need_have(amaas.api, ["parser"])
    @pytest.mark.parametrize("model_store", amaas.api.get_models_store("parser", DP.model_priority))
    def test_init_parser_model_store_run_with_default_params(self, model_store):
        """
        模型中心-parser: 默认参数检查 -> 运行 -> 停止, 只测试 1 卡, 且没有 scene
        """

        try:
            cs.launch_model(model_store, 1)
            cs.scene_and_stop(model_store, skip_scene=True)

        except Exception as e:
            logger.error(f"error occurred while testing parser: {e}")
            pytest.fail(f"error occurred while testing parser: {e}")

        finally:
            cs.stop(model_store, "parser")

    @Requires.need_have(amaas.api, ["audio"])
    @pytest.mark.parametrize("model_store", amaas.api.get_models_store("audio", DP.model_priority))
    def test_init_audio_model_store_run_with_default_params(self, model_store):
        """
        模型中心-audio: 默认参数检查 -> 运行 -> 停止, 只测试 1 卡, 且没有 scene
        """

        try:
            cs.launch_model(model_store, 1)
            cs.scene_and_stop(model_store, skip_scene=True)

        except Exception as e:
            logger.error(f"error occurred while testing audio: {e}")
            pytest.fail(f"error occurred while testing audio: {e}")

        finally:
            cs.stop(model_store, "audio")
