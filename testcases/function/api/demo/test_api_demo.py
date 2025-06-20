import json
from time import sleep
from random import randint
from appauto.manager.config_manager import LoggingConfig
from testcases.function.api.demo.gen_data import AMAAS

logger = LoggingConfig.get_logger()


def test_check_and_run_model_store():
    """
    embedding: 检测 -> 运行 -> 对话 -> 添加副本 -> 删除副本 -> 停止
    """
    # 获取模型静态资源
    model_stores = AMAAS.model_stores
    logger.info(f"total model stores: {len(model_stores)}")

    for m_s in model_stores:
        logger.info(m_s.object_id)

    # 对 embedding model 检测并运行
    embedding = AMAAS.embedding_model_stores[0]
    embedding.check()
    embedding.run()

    models = AMAAS.models

    logger.info(f"total models: {models}")

    for model in models:
        logger.info(f"model_data: {model.name}")

        for instance in model.instances:
            logger.info(json.dumps(instance.data))

    EMB_MODEL = [model for model in models if model.name == "bge-m3-FP16"][0]
    cur_rep = len(EMB_MODEL.instances)
    EMB_MODEL.set_replicas(cur_rep + 1)
    sleep(randint(5, 10))
    assert len(EMB_MODEL.instances) == cur_rep + 1

    EMB_MODEL.stop()


def test_chat_demo():
    """试验场景-对话"""
    # TODO 假设当前是存在的
    LLM_CHATS = AMAAS.llm_chats
    logger.info(f"total llm chats: {len(LLM_CHATS)}")

    CHAT = LLM_CHATS[0]
    # 获取原始 stream
    CHAT.talk("test", process_stream=False)
    # 获取 stream 对应文本
    CHAT.talk("test", process_stream=True)
