from random import choice

from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAMaaSLLMModelInstance:
    def test_llm_instance(self, amaas: AMaaS):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        for llm in amaas.model.llm:
            if inss := llm.instances:
                for ins in inss:
                    logger.info(ins.name)
                    logger.info(ins.object_id)
                    logger.info(ins.model_name)
                    logger.info(ins.model_id)
                    logger.info(ins.model)
                    logger.info(ins.worker)

    def test_vlm_instance(self, amaas: AMaaS):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        for vlm in amaas.model.vlm:
            if inss := vlm.instances:
                for ins in inss:
                    logger.info(ins.name)
                    logger.info(ins.object_id)
                    logger.info(ins.model_name)
                    logger.info(ins.model_id)
                    logger.info(ins.worker)

    def test_embedding_instance(self, amaas: AMaaS):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        for embedding in amaas.model.embedding:
            if inss := embedding.instances:
                for ins in inss:
                    logger.info(ins.name)
                    logger.info(ins.object_id)
                    logger.info(ins.model_name)
                    logger.info(ins.model_id)
                    logger.info(ins.worker)

    def test_rerank_instance(self, amaas: AMaaS):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        for rerank in amaas.model.rerank:
            if inss := rerank.instances:
                for ins in inss:
                    logger.info(ins.name)
                    logger.info(ins.object_id)
                    logger.info(ins.model_name)
                    logger.info(ins.model_id)
                    logger.info(ins.worker)

    def test_parser_instance(self, amaas: AMaaS):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        for parser in amaas.model.parser:
            if inss := parser.instances:
                for ins in inss:
                    logger.info(ins.name)
                    logger.info(ins.object_id)
                    logger.info(ins.model_name)
                    logger.info(ins.model_id)
                    logger.info(ins.worker)

    def test_audio_instance(self, amaas: AMaaS):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        for audio in amaas.model.audio:
            if inss := audio.instances:
                for ins in inss:
                    logger.info(ins.name)
                    logger.info(ins.object_id)
                    logger.info(ins.model_name)
                    logger.info(ins.model_id)
                    logger.info(ins.worker)
