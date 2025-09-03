from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestParserModelStorage:
    def test_parser_model_storage_check(self, amaas: AMaaS):
        parser_stores = amaas.init_model_store.parser
        logger.info(len(parser_stores))

        parser = parser_stores[0]
        worker_id = amaas.workers[0].object_id

        parser.check(worker_id=worker_id, tp=1)
        parser.run(worker_id=worker_id, tp=1)
