from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class TestAMaaSModel:
    def test_list_amaas_models(self, amaas: AMaaS):
        # TODO 将 amaas 抽出来
        # TODO 标记哪些 tests 是 ci
        if models := amaas.model.llm:
            assert models

            for model in models:
                logger.info(f"{model.name}".center(100, "*"))
                logger.info(f"data: {model.data}")
                logger.info(f"backend_parameters: {model.backend_parameters}")
                logger.info(f"backend_version: {model.backend_version}")

    def test_create_and_delete_replica(self, amaas: AMaaS):
        if models := amaas.model.llm:
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

    def test_stop_all_ins_and_llm_models(self, amaas: AMaaS):
        for model in amaas.model.llm:
            for ins in model.instances:

                logger.info(ins.name)
                logger.info(ins.object_id)
                logger.info(ins.object_tokens)
                logger.info(ins.OBJECT_TOKEN)
                logger.info(ins.model.name)

                ins.stop()

            model.stop()

    def test_stop_all_ins_and_vlm_models(self, amaas: AMaaS):
        for model in amaas.model.vlm:
            for ins in model.instances:

                logger.info(ins.name)
                logger.info(ins.object_id)
                logger.info(ins.object_tokens)
                logger.info(ins.OBJECT_TOKEN)
                logger.info(ins.model.name)

                ins.stop()

            model.stop()

    def test_stop_all_ins_and_embedding_models(self, amaas: AMaaS):
        for model in amaas.model.embedding:
            for ins in model.instances:

                logger.info(ins.name)
                logger.info(ins.object_id)
                logger.info(ins.object_tokens)
                logger.info(ins.OBJECT_TOKEN)
                logger.info(ins.model.name)

                ins.stop()

            model.stop()

    def test_stop_all_ins_and_rerank_models(self, amaas: AMaaS):
        for model in amaas.model.rerank:
            for ins in model.instances:

                logger.info(ins.name)
                logger.info(ins.object_id)
                logger.info(ins.object_tokens)
                logger.info(ins.OBJECT_TOKEN)
                logger.info(ins.model.name)

                ins.stop()

            model.stop()
