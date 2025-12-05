import allure
import pytest
from time import sleep
from random import sample

from appauto.validator.common import BaseValidator
from appauto.manager.config_manager import LoggingConfig

from testcases.sanity_check.ft.gen_data import amaas, ft_ctn, Defaultparams as DP


logger = LoggingConfig.get_logger()


@pytest.fixture(autouse=True)
def global_fixture_for_amaas_ci_sanity_check():
    # TODO 是否要优先 stop 所有模型
    amaas.wait_gpu_release()


@pytest.fixture(autouse=True, scope="session")
def worker_gpu_count():
    try:
        return amaas.gpu_sum
    except Exception:
        return 8


class CommonStep:
    @staticmethod
    @allure.step("check_gpu_count")
    def check_gpu_count(tp: int, total_gpu: int):
        if total_gpu < tp:
            pytest.skip(f"insufficent gpu count: {total_gpu} < {tp}")

    @staticmethod
    @allure.step("launch_model")
    def launch_model(model: str, tp: int):

        ft_ctn.launch_model_in_thread(model, tp, "correct", DP.ft_port, wait_for_running=True)

        assert ft_ctn.get_running_model_pids(ft_ctn.engine, model)
        sleep(5)

    @staticmethod
    @allure.step("scene_llm")
    def scene_llm(model: str, max_tokens: int = 2048, timeout=600):
        """
        llm: 提问 -> 检验是否有乱码
        """
        try:
            for q in sample(DP.llm_questions, 3):
                res = ft_ctn.api_server(DP.ft_port).talk_to_llm(q, model, max_tokens=max_tokens, timeout=timeout)
                BaseValidator.check_gibberish(res)
                return res

        except Exception as e:
            raise e

    @staticmethod
    @allure.step("scene_vlm")
    def scene_vlm(model: str, timeout=600):
        """
        vlm: 提问 -> 检验是否有乱码
        """
        try:
            res = ft_ctn.api_server(DP.ft_port).talk_to_vlm(model, image_path=DP.vlm_image_path, timeout=timeout)
            BaseValidator.check_gibberish(res)
            return res

        except Exception as e:
            logger.error(f"scene vlm failed. model: {model}, error: {str(e)}")
            raise e
