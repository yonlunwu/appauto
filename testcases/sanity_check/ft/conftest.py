import allure
import pytest


from appauto.validator.common import BaseValidator
from appauto.manager.config_manager import LoggingConfig

from testcases.sanity_check.ft.gen_data import amaas, Defaultparams as DP


logger = LoggingConfig.get_logger()


class CommonStep:
    def scene_llm(self, model: str, max_tokens: int = 2048, timeout=600):
        """
        llm: 提问 -> 检验是否有乱码
        """
        try:
            ft = amaas.docker_ctn_factory.ft
            for question in DP.llm_questions:
                res = ft.api_server(DP.ft_port).talk_to_llm(question, model, max_tokens=max_tokens, timeout=timeout)
                BaseValidator.check_gibberish(res)
                return res

        except Exception as e:
            raise e

    def scene_vlm(self, model: str, timeout=600):
        """
        vlm: 提问 -> 检验是否有乱码
        """
        try:
            ft = amaas.docker_ctn_factory.ft
            res = ft.api_server(DP.ft_port).talk_to_vlm(model, image_path=DP.vlm_image_path, timeout=timeout)
            BaseValidator.check_gibberish(res)
            return res

        except Exception as e:
            logger.error(f"scene vlm failed. model: {model}, error: {str(e)}")
            raise e
