from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig


logger = LoggingConfig.get_logger()


class TestAMaaSSceneRerank:
    def test_rerank_chat(self, amaas: AMaaS):

        for rerank in amaas.scene.rerank:
            logger.info(f"{rerank.data}".center(200, "="))
            logger.info(f"{rerank.object_id}".center(100, "="))
            logger.info(f"{rerank.display_model_name}".center(100, "="))
            logger.info(f"{rerank.object}".center(100, "="))
            logger.info(f"{rerank.owned_by}".center(100, "="))

            res = rerank.talk()
            logger.info(f"get response of disable_stream and encode_result: {res}")
