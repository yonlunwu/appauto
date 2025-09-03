from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig


logger = LoggingConfig.get_logger()


class TestAMaaSSceneVLM:
    def test_vlm_chat(self, amaas: AMaaS):

        for vlm in amaas.scene.vlm:
            logger.info(f"{vlm.data}".center(200, "="))
            logger.info(f"{vlm.object_id}".center(100, "="))
            logger.info(f"{vlm.display_model_name}".center(100, "="))
            logger.info(f"{vlm.object}".center(100, "="))
            logger.info(f"{vlm.owned_by}".center(100, "="))

            res = vlm.talk(stream=True)
            logger.info(f"get response of disable_stream and encode_result: {res}")
            res = vlm.talk(stream=False)
            logger.info(f"get response of disable_stream and encode_result: {res}")
