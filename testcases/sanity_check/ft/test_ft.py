import allure
import pytest
from time import sleep

from appauto.manager.config_manager import LoggingConfig
from appauto.manager.utils_manager import Requires

from testcases.sanity_check.ft.gen_data import amaas, Defaultparams as DP
from testcases.sanity_check.ft.conftest import CommonStep as cs

logger = LoggingConfig.get_logger()


class Test_Sanity_Check_FT_Base_Action_With_Default:
    @pytest.mark.parametrize("model", amaas.select_local_models(DP.model_priority, "llm"))
    @pytest.mark.parametrize("tp", DP.tp)
    def test_llm_run_with_default_params(self, tp, model):
        """
        llm: 默认参数检查 -> 运行 -> 试验场景
        """

        if model != "DeepSeek-V3-0324-GPU-weight":
            pytest.skip(f"model {model} is not DeepSeek-V3-0324-GPU-weight.")

        ft_ctn = amaas.docker_ctn_factory.ft
        ft_ctn.launch_model_in_thread(model, tp, "correct", DP.ft_port, wait_for_running=True)

        assert ft_ctn.get_running_model_pids(ft_ctn.engine, model)
        sleep(5)

        for question in DP.llm_questions:
            cs.scene_llm(question, model)

        ft_ctn.stop_model(model)

    @pytest.mark.parametrize("model", amaas.select_local_models(DP.model_priority, "vlm"))
    @pytest.mark.parametrize("tp", DP.tp)
    def test_vlm_run_with_default_params(self, tp, model):
        """
        vlm: 默认参数检查 -> 运行 -> 试验场景
        """
        if model != "GLM-4.5V-GPU-weight":
            pytest.skip(f"model {model} is not GLM-4.5V-GPU-weight.")

        ft_ctn = amaas.docker_ctn_factory.ft
        ft_ctn.launch_model_in_thread(model, tp, "correct", DP.ft_port, wait_for_running=True)

        assert ft_ctn.get_running_model_pids(ft_ctn.engine, model)
        sleep(5)

        # TODO 这里需要改成图片输入
        for question in DP.llm_questions:
            cs.scene_llm(question, model)

        ft_ctn.stop_model(model)
