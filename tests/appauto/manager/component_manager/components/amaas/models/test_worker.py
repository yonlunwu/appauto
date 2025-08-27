from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAMaaSWorker:
    def test_list_amaas_workers(self):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        amaas = AMaaS("120.211.1.45", port=10001, username="admin", passwd="123456")
        assert amaas

        if workers := amaas.workers:
            assert workers

            for worker in workers:
                logger.info(worker.data)
                logger.info(worker.name)

    def test_get_worker_attr(self):
        amaas = AMaaS("120.211.1.45", port=10001, username="admin", passwd="123456")
        assert amaas

        if workers := amaas.workers:
            assert workers

            for worker in workers:
                logger.info(worker.name)
                logger.info(worker.gpu_empty_count)
                logger.info(worker.gpu_sum)
                logger.info(worker.cache_capacity)
                logger.info(worker.cache_total)
                logger.info(worker.cache_used)
                logger.info(worker.cache_available)
