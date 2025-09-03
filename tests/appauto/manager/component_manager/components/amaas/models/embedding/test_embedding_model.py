from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestEmbeddingModel:
    def test_embedding_model_create_replica(self, amaas: AMaaS):
        embeddings = amaas.model.embedding
        logger.info(len(embeddings))

        embedding = embeddings[0]
        worker_id = amaas.workers[0].object_id

        embedding.check(worker_id=worker_id, tp=1)
        embedding.create_replica(worker_id=worker_id, tp=1)

    def test_embedding_model_stop(self, amaas: AMaaS):
        embeddings = amaas.model.embedding
        logger.info(len(embeddings))

        embedding = embeddings[0]

        for ins in embedding.instances:
            logger.info(f"instance.object_id: {ins.object_id}".center(100, "*"))

        # 删除副本
        ins.stop()

        # 模型停止运行
        embedding.stop()
