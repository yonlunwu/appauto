from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestRerankModel:
    def test_rerank_model_create_replica(self, amaas: AMaaS):
        reranks = amaas.model.rerank
        logger.info(len(reranks))

        rerank = reranks[0]
        worker_id = amaas.workers[0].object_id

        rerank.check(worker_id=worker_id, tp=1)
        rerank.create_replica(worker_id=worker_id, tp=1)

    def test_rerank_model_stop(self, amaas: AMaaS):
        reranks = amaas.model.rerank
        logger.info(len(reranks))

        rerank = reranks[0]

        for ins in rerank.instances:
            logger.info(f"instance.object_id: {ins.object_id}".center(100, "*"))

        # 删除副本
        ins.stop()

        # 模型停止运行
        rerank.stop()
