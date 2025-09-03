from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestRerankModelStorage:
    def test_parser_model_storage_check(self, amaas: AMaaS):
        assert amaas

        rerank_stores = amaas.init_model_store.rerank
        logger.info(len(rerank_stores))

        rerank = rerank_stores[0]
        worker_id = amaas.workers[0].object_id

        rerank.check(worker_id=worker_id, tp=1)
        rerank.run(worker_id=worker_id, tp=1)
