from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestParserModel:
    def test_parser_model_create_replica(self, amaas: AMaaS):
        parsers = amaas.model.parser
        logger.info(len(parsers))

        parser = parsers[0]
        worker_id = amaas.workers[0].object_id

        parser.check(worker_id=worker_id, tp=1)
        parser.create_replica(worker_id=worker_id, tp=1)

    def test_parser_model_stop(self, amaas: AMaaS):
        parsers = amaas.model.parser
        logger.info(len(parsers))

        parser = parsers[0]

        for ins in parser.instances:
            logger.info(f"instance.object_id: {ins.object_id}".center(100, "*"))

        # 删除副本
        ins.stop()

        # 模型停止运行
        parser.stop()
