"""
测试 model 的请求分发是否满足负载均衡
"""

import allure
from functools import partial
from concurrent.futures import Future, wait
from uuid import uuid4

from appauto.manager.config_manager import LoggingConfig
from appauto.manager.utils_manager import Requires
from appauto.manager.utils_manager.custom_thread_pool_executor import CustomThreadPoolExecutor, check_futures_exception


from testcases.amaas.gen_data import amaas, DefaultParams as DP
from testcases.amaas.api.conftest import CommonModelPerformenceStep as cps

logger = LoggingConfig.get_logger()


def callback(future: Future, func: callable, raise_exception: bool = False):
    res = None
    try:
        res = future.result()
        logger.info(f"{func.__qualname__} succeed, result: {res}")
    except Exception as e:
        logger.info(f"{func.__qualname__} failed, result: {res}")
        if raise_exception:
            raise e


@allure.epic("TestAMaaSModelBatchQuery")
class TestAMaaSModelBatchQuery:
    @Requires.need_have(amaas, ["llm"])
    def test_batch_query_llm(self):
        """
        并发 query llm. 当前无法到对应主机查看引擎日志, 需要人为查看
        TODO 可以加上去 supervisor 节点查看 backend/server.log
        """
        llm = [chat for chat in amaas.scene.llm if chat.object_id == DP.model_name][0]
        fus = []

        with CustomThreadPoolExecutor(max_workers=DP.concurrency) as executor:
            for _ in range(DP.query_count):
                fu = executor.submit(llm.talk, str(uuid4()), max_tokens=128)
                # fu = executor.submit(llm.talk, cps.gen_text_with_length(int(DP.prompt_length)), max_tokens=128)
                fu.add_done_callback(partial(callback, func=self.test_batch_query_llm, raise_exception=True))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

    @Requires.need_have(amaas, ["embedding"])
    def test_batch_query_embedding(self):
        """
        并发 query embedding. 当前无法到对应主机查看引擎日志, 需要人为查看
        TODO 可以加上去 supervisor 节点查看 backend/server.log
        """
        chat = [chat for chat in amaas.scene.embedding if chat.object_id == "bge-m3-FP16"][0]
        fus = []

        with CustomThreadPoolExecutor(max_workers=DP.concurrency) as executor:
            for i in range(DP.query_count):

                fu = executor.submit(chat.talk, ["橘子", "香蕉", "苹果", "公司"], compute_similarity=True)
                fu.add_done_callback(partial(callback, func=self.test_batch_query_embedding, raise_exception=True))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

    @Requires.need_have(amaas, ["rerank"])
    def test_batch_query_rerank(self):
        """
        并发 query rerank. 当前无法到对应主机查看引擎日志, 需要人为查看
        TODO 可以加上去 supervisor 节点查看 backend/server.log
        """
        chat = [chat for chat in amaas.scene.rerank if chat.object_id == "bge-reranker-v2-m3"][0]
        fus = []

        with CustomThreadPoolExecutor(max_workers=DP.concurrency) as executor:
            for i in range(DP.query_count):

                fu = executor.submit(chat.talk)
                fu.add_done_callback(partial(callback, func=self.test_batch_query_rerank, raise_exception=True))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

    @Requires.need_have(amaas, ["vlm"])
    def test_batch_query_vlm(self):
        """
        并发 query vlm. 当前无法到对应主机查看引擎日志, 需要人为查看
        TODO 可以加上去 supervisor 节点查看 backend/server.log
        """
        chat = [chat for chat in amaas.scene.vlm if chat.display_model_name == "Qwen2.5-VL-7B-Instruct"][0]
        fus = []

        with CustomThreadPoolExecutor(max_workers=DP.concurrency) as executor:
            for i in range(DP.query_count):

                fu = executor.submit(
                    chat.talk,
                    "请解释这张图片",
                    image_path="/Users/ryanyang/Desktop/WechatIMG1.jpeg",
                    stream=True,
                    process_stream=True,
                )
                fu.add_done_callback(partial(callback, func=self.test_batch_query_vlm, raise_exception=True))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)
