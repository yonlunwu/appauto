from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig


logger = LoggingConfig.get_logger()


class TestAMaaSScene:
    def test_model_stores(self):
        amaas = AMaaS("117.133.60.227", port=10001, username="yanlong", passwd="HC!r0cks")
        assert amaas

        assert amaas.llm_model_stores
        assert amaas.vlm_model_stores
        assert amaas.embedding_model_stores
        assert amaas.parser_model_stores
        assert amaas.audio_model_stores

    def test_chat(self):
        amaas = AMaaS("120.211.1.45", port=10001)

        for chat in amaas.llm_chats:
            logger.info(f"{chat.data}".center(200, "="))
            logger.info(f"{chat.object_id}".center(100, "="))
            logger.info(f"{chat.display_model_name}".center(100, "="))
            logger.info(f"{chat.object}".center(100, "="))
            logger.info(f"{chat.owned_by}".center(100, "="))
