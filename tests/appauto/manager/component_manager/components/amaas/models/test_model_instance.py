from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAMaaSModelInstance:
    def test_instance_worker_gpu(self):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        amaas = AMaaS("120.211.1.45", port=10001, username="admin", passwd="123456")
        assert amaas

        for model in amaas.models:
            logger.info(f"{model.name}".center(100, "*"))

            for ins in model.instances:
                logger.info(f"{ins.name}".center(100, "*"))
                logger.info(ins.gpus)

                for gpu in ins.gpus:
                    logger.info(f"{gpu.name}".center(100, "*"))
                    logger.info(f"{gpu.index}".center(100, "*"))
                    logger.info(f"{gpu.object_id}".center(100, "*"))

                logger.info(f"{ins.worker}")
                logger.info(f"{ins.worker.object_id}".center(100, "*"))
                logger.info(f"{ins.worker.name}".center(100, "*"))
