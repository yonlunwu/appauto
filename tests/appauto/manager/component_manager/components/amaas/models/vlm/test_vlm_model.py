from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestVLMModel:
    def test_vlm_model_create_replica(self, amaas: AMaaS):
        vlms = amaas.model.vlm
        logger.info(len(vlms))

        vlm = vlms[0]
        worker_id = amaas.workers[0].object_id

        vlm.check(worker_id=worker_id, tp=1)
        vlm.create_replica(worker_id=worker_id, tp=1)

    def test_vlm_model_stop(self, amaas: AMaaS):
        vlms = amaas.model.vlm
        logger.info(len(vlms))

        vlm = vlms[0]

        for ins in vlm.instances:
            logger.info(f"instance.object_id: {ins.object_id}".center(100, "*"))

        # 删除副本
        ins.stop()

        # 模型停止运行
        vlm.stop()
