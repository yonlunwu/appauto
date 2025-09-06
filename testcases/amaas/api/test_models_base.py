"""
测试 models 的默认参数检查 / 运行 / 试验场景 / 停止
"""

import pytest
import allure

from appauto.manager.config_manager import LoggingConfig

from testcases.amaas.gen_data import amaas, DefaultParams as DP
from testcases.amaas.api.conftest import (
    CommonModelBaseRunner as cr,
    DoCheck as dc,
)

logger = LoggingConfig.get_logger()


@allure.epic("TestAMaaSModelBaseAction")
class TestAMaaSModelBaseAction:

    @pytest.mark.parametrize("model_store_type", DP.init_model_store_type)
    def test_check_run_and_scene_init_model_store_under_default_params(self, model_store_type):
        """
        模型中心: 默认参数检查 -> 运行 -> 试验场景 (试验场的对话内容需要人为查看是否有乱码), \
            遍历 ["llm", "vlm", "embedding", "rerank", "parser", "audio"]
        """
        models_store = getattr(amaas.init_model_store, model_store_type)

        items = []

        # TODO 根据 tp 和 m_s 分成多个用例
        tps = [1] if model_store_type in ["parser", "audio"] else [1, 2, 4, 8]

        for m_s in models_store:
            item = {}
            cr.check_and_run_default_params_under_diff_tp(tps, items, item, m_s)

        dc.check_final_items(items)
