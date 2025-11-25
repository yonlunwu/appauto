from appauto.operator import AMaaSNode
from appauto.organizer.model_params.constructor import AMaaSModelParams
from appauto.manager.config_manager.config_logging import LoggingConfig


logger = LoggingConfig.get_logger()


IP = "192.168.110.4"
USER = "qujing"

amaas = AMaaSNode(IP, USER, skip_cli=True)


class TestAmaaSModelParams:
    def test_nvidia_deepseek_v3_0324(self):
        tp = 1
        tp = 2
        model_name = "DeepSeek-V3-0324-GPU-weight"
        model_store = amaas.api.init_model_store.llm.filter(name=model_name)[0]
        params = AMaaSModelParams(amaas, model_store, tp).gen_default_params

        logger.info(params)

        amaas.api.launch_model_with_default(tp, model_store)
