"""
测试 models 的检查 / 运行 / 停止
"""

import pytest
from uuid import uuid4
from time import sleep, time
from random import randint
from concurrent.futures import Future, wait
from functools import partial

from appauto.manager.config_manager import LoggingConfig
from appauto.manager.utils_manager import CustomThreadPoolExecutor, check_futures_exception

from testcases.amaas.gen_data import amaas, DefaultParams as DP
from testcases.amaas.api.conftest import (
    CommonRunTestAMaaSAPI as cr,
    CommonStepModelAction as cs,
    CommonCheckAMaaSAPI as cc,
)

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


class TestModelsBaseOption:
    def test_llm_base_option(self):
        """
        - 测试点: 遍历 llm model_stores
            默认参数检测 -> 运行 -> 对话（提问 4 个问题）-> 能收到回答且模型不会挂(且内容预期没有乱码或死循环等基础问题)\
                -> 停止 -> 确认资源回收(pid / nvidia-smi / api 获取 gpu 资源)
        """
        failed_models = []
        timeout_s = 600

        # 获取模型中心 llm
        model_stores = [mod for mod in amaas.llm_model_stores if mod.source == "init"]
        logger.info(f"total model stores: {len(model_stores)}".center(100, "="))

        for mod in model_stores:
            logger.info(f"model: {mod.name}, begin".center(100, "="))

            rule = mod.get_run_rule()

            # TODO check 不通过的也应该加入 failed
            logger.info(f"model: {mod.name}, check".center(100, "="))
            res = mod.check(access_limit=rule.data.access_limit, max_total_tokens=rule.data.max_total_tokens, tp=2)
            logger.info(f"model: {mod.name}, check result: {res}".center(300, "="))

            # TODO run 不通过的也应该加入 failed
            logger.info(f"model: {mod.name}, run".center(100, "="))
            res = mod.run(access_limit=rule.data.access_limit, max_total_tokens=rule.data.max_total_tokens, tp=2)
            logger.info(f"model: {mod.name}, run result: {res}".center(300, "="))

            start_time = time()

            # 等待成功拉起
            while True:
                model = [model for model in amaas.models if model.name == mod.name][0]
                if time() - start_time >= timeout_s:
                    failed_models.append(mod.name)
                    logger.error(f"model: {mod.name}, running failed: timeout".center(100, "="))
                    raise TimeoutError(f"Timeout while waiting for {mod.name} running.")

                if model.status == "running":
                    logger.info(f"model: {mod.name}, running succeed".center(100, "="))
                    break

                elif model.status == "error":
                    logger.info(f"model: {mod.name}, running failed: error".center(100, "="))
                    break

                elif model.status == "loading":
                    logger.info(f"model: {mod.name}, still loading".center(100, "="))
                    sleep(30)
                    continue

            sleep(randint(10, 30))

            # 拉起后提问
            chat = [chat for chat in amaas.llm_chats if chat.object_id == mod.name][0]

            logger.info(f"{chat.data}".center(200, "="))
            logger.info(f"{chat.object_id}".center(100, "="))
            logger.info(f"{chat.display_model_name}".center(100, "="))
            logger.info(f"{chat.object}".center(100, "="))
            logger.info(f"{chat.owned_by}".center(100, "="))

            res = chat.talk("测试", stream=False, encode_result=True)
            logger.info(f"get response of disable_stream and encode_result: {res}")
            res = chat.talk("test", stream=True, process_stream=False)
            logger.info(f"get response of enable_stream and not_process_stream: {res}")

            # 停止运行
            model.stop()
            logger.info(f"model: {mod.name}, test pass".center(100, "="))

        logger.info(f"failed_models: {failed_models}")
        assert not failed_models

    def test_batch_query_llm(self):
        # chat = [chat for chat in amaas.llm_chats if chat.object_id == "DeepSeek-R1-0528-GPU-weight"][0]
        chat = [chat for chat in amaas.llm_chats if chat.object_id == "Qwen2.5-32B-Instruct-GPTQ-Int8"][0]
        fus = []

        with CustomThreadPoolExecutor(max_workers=DP.concurrency) as executor:
            for i in range(DP.query_count):
                # fu = executor.submit(chat.talk, "python vs go", stream=False, encode_result=True, max_tokens=128)
                fu = executor.submit(chat.talk, str(uuid4()), stream=False, encode_result=True, max_tokens=64)
                fu.add_done_callback(partial(callback, func=self.test_batch_query_llm, raise_exception=True))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

    def test_batch_query_embedding(self):
        chat = [chat for chat in amaas.embedding_chats if chat.object_id == "bge-m3-FP16"][0]
        fus = []

        with CustomThreadPoolExecutor(max_workers=DP.concurrency) as executor:
            for i in range(DP.query_count):

                # fu = executor.submit(chat.talk, str(uuid4()), compute_similarity=True)
                fu = executor.submit(chat.talk, ["橘子", "香蕉", "苹果", "公司"], compute_similarity=True)
                fu.add_done_callback(partial(callback, func=self.test_batch_query_embedding, raise_exception=True))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

    def test_batch_query_rerank(self):
        chat = [chat for chat in amaas.rerank_chats if chat.object_id == "bge-reranker-v2-m3"][0]
        fus = []

        with CustomThreadPoolExecutor(max_workers=DP.concurrency) as executor:
            for i in range(DP.query_count):

                fu = executor.submit(chat.talk)
                fu.add_done_callback(partial(callback, func=self.test_batch_query_rerank, raise_exception=True))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

    def test_batch_query_multi_model(self):
        chat = [chat for chat in amaas.multi_model_chats if chat.display_model_name == "Qwen2.5-VL-7B-Instruct-AWQ"][0]
        fus = []

        with CustomThreadPoolExecutor(max_workers=DP.concurrency) as executor:
            for i in range(DP.query_count):

                fu = executor.submit(
                    chat.talk,
                    "请解释这张图片",
                    image_path="/Users/ryanyang/Desktop/WechatIMG1.jpeg",
                    stream=True,
                    process_stream=True,
                    # stream=False,
                    # encode_result=True,
                )
                fu.add_done_callback(partial(callback, func=self.test_batch_query_multi_model, raise_exception=True))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

    def test_batch_query_moe_same_node(self):
        # r1_0528 = [mod for mod in amaas.models if mod.name == "DeepSeek-R1-0528-GPU-weight"][0]
        # kimi_k2 = [mod for mod in amaas.models if mod.name == "Kimi-K2-1000B-INT4"][0]

        r1_0528 = [mod for mod in amaas.llm_chats if mod.display_model_name == "DeepSeek-R1-0528-GPU-weight"][0]
        kimi_k2 = [mod for mod in amaas.llm_chats if mod.display_model_name == "Kimi-K2-1000B-INT4"][0]

        fus = []

        with CustomThreadPoolExecutor() as executor:
            fu1 = executor.submit(r1_0528.talk, "请告诉我关于北京和历史", stream=False, encode_result=True)
            fu2 = executor.submit(kimi_k2.talk, "python fastapi", stream=False, encode_result=True)
            fus = [fu1, fu2]

        wait(fus)

        check_futures_exception(fus)
