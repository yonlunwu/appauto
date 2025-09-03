from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestVLMModelStorage:
    def test_vlm_model_storage_check(self, amaas: AMaaS):
        vlm_stores = amaas.init_model_store.vlm
        logger.info(len(vlm_stores))

        vlm = vlm_stores[0]
        worker_id = amaas.workers[0].object_id

        vlm.check(worker_id=worker_id, tp=1)
        vlm.run(worker_id=worker_id, tp=1)
