from random import choice

from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestLLMModel:
    def test_llm_model_create_replica(self, amaas: AMaaS):
        llms = amaas.model.llm
        logger.info(len(llms))

        # llm = [llm for llm in llms if llm.name == "DeepSeek-R1-0528-GPU-weight"][0]
        for llm in llms:
            # worker_id = [w.object_id for w in amaas.workers if w.name == "zkyd_46"][0]
            worker_id = choice(amaas.workers).object_id

            llm.check(worker_id=worker_id, tp=1)

            ins = llm.create_replica(worker_id=worker_id, tp=1, wait_for_running=True)
            logger.info(ins.name)
            logger.info(ins.object_id)
            logger.info(ins.state)

    def test_llm_model_stop(self, amaas: AMaaS):
        llms = amaas.model.llm
        logger.info(len(llms))

        llm = llms[0]

        for ins in llm.instances:
            logger.info(f"instance.object_id: {ins.object_id}".center(100, "*"))

        # 删除副本
        ins.stop()

        # 模型停止运行
        llm.stop()
