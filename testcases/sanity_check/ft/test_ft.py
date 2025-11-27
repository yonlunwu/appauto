"""
基于 zhiwen-ft 执行 sanity_check.
"""

import allure
import pytest

from appauto.manager.config_manager import LoggingConfig
from appauto.manager.utils_manager import Requires

from testcases.sanity_check.ft.gen_data import amaas, ft_ctn, Defaultparams as DP
from testcases.sanity_check.ft.conftest import CommonStep as cs

logger = LoggingConfig.get_logger()


@allure.epic("Test_Sanity_Check_FT_Base_Action_With_Default")
@pytest.mark.ft_ci_sanity_check
class Test_Sanity_Check_FT_Base_Action_With_Default:
    @pytest.mark.parametrize("model", amaas.select_local_models(DP.model_priority, "llm"))
    @pytest.mark.parametrize("tp", DP.tp)
    def test_llm_run_with_default_params(self, tp, model, worker_gpu_count):
        """
        llm: 默认参数检查 -> 运行 -> 试验场景
        """
        cs.check_gpu_count(tp, worker_gpu_count)

        try:
            cs.launch_model(model, tp)
            cs.scene_llm(model)

        except Exception as e:
            logger.error(f"error occurred while testing llm: {e}")
            pytest.fail(f"error occurred while testing llm: {e}")

        finally:
            ft_ctn.stop_model(model)

    @pytest.mark.parametrize("model", amaas.select_local_models(DP.model_priority, "vlm"))
    @pytest.mark.parametrize("tp", DP.tp)
    def test_vlm_run_with_default_params(self, tp, model, worker_gpu_count):
        """
        vlm: 默认参数检查 -> 运行 -> 试验场景
        """
        cs.check_gpu_count(tp, worker_gpu_count)

        try:
            cs.launch_model(model, tp)
            cs.scene_vlm(model)

        except Exception as e:
            logger.error(f"error occurred while testing vlm: {e}")
            pytest.fail(f"error occurred while testing vlm: {e}")

        finally:
            ft_ctn.stop_model(model)
