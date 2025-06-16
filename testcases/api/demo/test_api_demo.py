import json
from time import sleep
from random import randint
from appauto.manager.config_manager.config_logging import LoggingConfig
from testcases.api.demo.gen_data import KLLM

logger = LoggingConfig.get_logger()


def test_check_and_run_model_store():
    """
    embedding: 检测 -> 运行 -> 添加副本 -> 删除副本 -> 停止
    """
    assert len(KLLM.model_stores) == 15

    for m_i in KLLM.model_stores:
        logger.info(m_i.object_id)

    embedding_model_store = [model for model in KLLM.model_stores if model.data.name == "bge-m3-FP16"][0]
    embedding_model_store.check()
    embedding_model_store.run()

    assert KLLM.models

    for model in KLLM.models:
        logger.info(json.dumps(model.data))

        for instance in model.instances:
            logger.info(json.dumps(instance.data))

        cur_rep = len(model.instances)
        model.set_replicas(cur_rep + 1)
        sleep(randint(5, 10))
        assert len(model.instances) == cur_rep + 1

        model.stop()

    model = [model for model in KLLM.models if model]
