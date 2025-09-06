"""
测试 moe models 的并发访问控制
"""

import allure
from concurrent.futures import wait

from appauto.manager.utils_manager.custom_thread_pool_executor import CustomThreadPoolExecutor, check_futures_exception

from testcases.amaas.gen_data import amaas


@allure.epic("TestAMaaSMoEModelConcurrencyAccessManagement")
class TestAMaaSMoEModelConcurrencyAccessManagement:
    def test_batch_query_moe_same_node(self):
        """
        场景: 同一节点起 2 个不同的 MoE 模型并同时发请求, 预期同一时刻只有 1 个 MoE 能提供服务.
        """
        r1_0528 = [mod for mod in amaas.scene.llm if mod.display_model_name == "DeepSeek-R1-0528-GPU-weight"][0]
        kimi_k2 = [mod for mod in amaas.scene.llm if mod.display_model_name == "Kimi-K2-1000B-INT4"][0]

        fus = []

        with CustomThreadPoolExecutor() as executor:
            fu1 = executor.submit(r1_0528.talk, "请告诉我关于北京和历史", stream=False, encode_result=True)
            fu2 = executor.submit(kimi_k2.talk, "python fastapi", stream=False, encode_result=True)
            fus = [fu1, fu2]

        wait(fus)

        check_futures_exception(fus)
