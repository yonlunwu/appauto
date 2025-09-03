from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAMaaSWorker:
    def test_list_amaas_workers(self, amaas: AMaaS):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        if workers := amaas.workers:
            assert workers

            for worker in workers:
                logger.info(worker.data)
                logger.info(worker.name)
                logger.info(worker.object_id)

    def test_get_worker_attr(self, amaas: AMaaS):
        if workers := amaas.workers:
            assert workers

            for worker in workers:
                logger.info(worker.amaas)
                logger.info(worker.name)
                logger.info(worker.object_id)
                logger.info(worker.gpu_empty_count)
                logger.info(worker.gpu_sum)
                logger.info(worker.cache_capacity)
                logger.info(worker.cache_total)
                logger.info(worker.cache_used)
                logger.info(worker.cache_available)

    def test_get_worker_model_instances_obj(self, amaas: AMaaS):
        for worker in amaas.workers:
            logger.info(worker.name)
            logger.info(worker.model_instances)
            logger.info(worker.amaas.model.llm)

            for ins in worker.llm_instances_obj:
                logger.info(ins.name)
                logger.info(ins.object_id)
                logger.info(ins)
