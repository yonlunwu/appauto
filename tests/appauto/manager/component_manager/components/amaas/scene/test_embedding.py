from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig


logger = LoggingConfig.get_logger()


class TestAMaaSSceneEmbedding:
    def test_embedding_chat(self, amaas: AMaaS):

        for embed in amaas.scene.embedding:
            logger.info(f"{embed.data}".center(200, "="))
            logger.info(f"{embed.object_id}".center(100, "="))
            logger.info(f"{embed.display_model_name}".center(100, "="))
            logger.info(f"{embed.object}".center(100, "="))
            logger.info(f"{embed.owned_by}".center(100, "="))

            res = embed.talk(["橘子", "香蕉", "苹果", "公司"], compute_similarity=True)
            logger.info(res)
