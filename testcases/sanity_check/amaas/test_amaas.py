"""
基于 amaas 执行 sanity_check.
"""

import allure
import pytest

from appauto.manager.config_manager import LoggingConfig
from appauto.manager.utils_manager import Requires
from appauto.manager.error_manager.errors import OperationNotSupported


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
