from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestLLMModelStorage:
    def test_llm_model_storage_check(self, amaas: AMaaS):
        llm_stores = amaas.init_model_store.llm
        logger.info(len(llm_stores))

        llm = llm_stores[0]
        worker_id = amaas.workers[0].object_id

        llm.check(worker_id=worker_id, tp=1)
        llm.run(worker_id=worker_id, tp=1)
