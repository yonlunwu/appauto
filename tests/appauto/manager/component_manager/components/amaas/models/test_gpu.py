from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAMaaSWorkerGPU:
    def test_list_worker_gpus(self):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        amaas = AMaaS("120.211.1.45", port=10001, username="admin", passwd="123456")
        assert amaas

        workers = amaas.workers
        assert workers

        for worker in workers:
            logger.info(f"{worker.name}".center(100, "*"))
            logger.info(worker.data)
            logger.info(worker.object_id)

            logger.info(worker.gpus)

    def test_list_gpu_model_instance_ids(self):
        amaas = AMaaS("120.211.1.45", port=10001, username="admin", passwd="123456")
        assert amaas

        for worker in amaas.workers:
            for gpu in worker.gpus:
                logger.info(gpu.name)
                logger.info(gpu)
                logger.info(gpu.object_id)
                logger.info(gpu.data)
                logger.info(gpu.worker)

                logger.info(gpu.model_instances)

                ins_objs = gpu.model_instances_obj
                logger.info(ins_objs)

                if ins_objs:
                    for obj in ins_objs:
                        logger.info(f"{obj.name}".center(100, "*"))
                        logger.info(obj.object_id)
