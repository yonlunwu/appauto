from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestEmbeddingModelStorage:
    def test_embedding_model_storage_check(self, amaas: AMaaS):

        embedding_stores = amaas.init_model_store.embedding
        logger.info(len(embedding_stores))

        embedding = embedding_stores[0]
        worker_id = amaas.workers[0].object_id

        embedding.check(worker_id=worker_id, tp=1)
        embedding.run(worker_id=worker_id, tp=1)
