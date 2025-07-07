from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig


logger = LoggingConfig.get_logger()


class TestAMaaS:
    def test_model_stores(self):
        amaas = AMaaS("117.133.60.227", port=10001, username="yanlong", passwd="HC!r0cks")
        assert amaas

        assert amaas.llm_model_stores
        assert amaas.vlm_model_stores
        assert amaas.embedding_model_stores
        assert amaas.parser_model_stores
        assert amaas.audio_model_stores
