from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig


logger = LoggingConfig.get_logger()


class TestAMaaSSceneLLM:
    def test_llm_chat(self, amaas: AMaaS):

        for llm in amaas.scene.llm:
            logger.info(f"{llm.data}".center(200, "="))
            logger.info(f"{llm.object_id}".center(100, "="))
            logger.info(f"{llm.display_model_name}".center(100, "="))
            logger.info(f"{llm.object}".center(100, "="))
            logger.info(f"{llm.owned_by}".center(100, "="))

            res = llm.talk("测试", stream=False, encode_result=True)
            logger.info(f"get response of disable_stream and encode_result: {res}")
            res = llm.talk("test", stream=True, process_stream=False)
            logger.info(f"get response of enable_stream and not_process_stream: {res}")
            res = llm.talk("test", stream=True, process_stream=True)
            logger.info(f"get response of enable_stream and process_stream: {res}")
