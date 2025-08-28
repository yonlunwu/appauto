from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAMaaSModel:
    def test_list_amaas_models(self):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        amaas = AMaaS("120.211.1.45", port=10001, username="admin", passwd="123456")
        assert amaas

        if models := amaas.models:
            assert models

            for model in models:
                logger.info(f"{model.name}".center(100, "*"))
                logger.info(f"data: {model.data}")
                logger.info(f"backend_parameters: {model.backend_parameters}")
                logger.info(f"backend_version: {model.backend_version}")

    def test_get_worker_attr(self):
        amaas = AMaaS("120.211.1.45", port=10001, username="admin", passwd="123456")
        assert amaas

        if workers := amaas.workers:
            assert workers

            for worker in workers:
                logger.info(worker.amaas)
                logger.info(worker.name)
                logger.info(worker.gpu_empty_count)
                logger.info(worker.gpu_sum)
                logger.info(worker.cache_capacity)
                logger.info(worker.cache_total)
                logger.info(worker.cache_used)
                logger.info(worker.cache_available)

    def test_create_and_delete_replica(self):
        amaas = AMaaS("120.211.1.45", port=10001, username="admin", passwd="123456")
        assert amaas

        if models := amaas.models:
            assert models

            works = amaas.workers
            for work in works:
                logger.info(work.name)
                logger.info(work.object_id)

            for model in models:
                logger.info(f"{model.name}".center(100, "*"))
                logger.info(f"data: {model.data}")

                model.check(worker_id=work.object_id, tp=2)
                new_ins = model.create_replica(worker_id=work.object_id, tp=2)
                logger.info(new_ins)
                logger.info(new_ins.data)
                logger.info(new_ins.object_id)
                logger.info(new_ins.name)

                for ins in model.instances:
                    logger.info(f"{ins.name}".center(100, "="))
                    logger.info(f"data: {ins.data}")
                    logger.info(f"object_id: {ins.object_id}")

                ins.stop()

                for ins in model.instances:
                    logger.info(f"{ins.name}".center(100, "="))
                    logger.info(f"data: {ins.data}")
                    logger.info(f"object_id: {ins.object_id}")
