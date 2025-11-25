from appauto.operator import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig


logger = LoggingConfig.get_logger()


IP = "192.168.111.10"
USER = "qujing"

amaas = AMaaSNode(IP, USER).api


class TestAmaaSModelParams:
    def test_launch_model_with_default(self):
        tp = 1
        tp = 2
        model_name = "DeepSeek-V3-0324-GPU-weight"
        model_store = amaas.init_model_store.llm.filter(name=model_name)[0]

        amaas.launch_model_with_default(tp, model_store)

    def test_wait_gpu_release(self):
        amaas.wait_gpu_release()

    def test_launch_model_with_perf(self):
        tp = 2
        model_name = "DeepSeek-R1-0528-GPU-weight"
        model_store = amaas.init_model_store.llm.filter(name=model_name)[0]

        amaas.launch_model_with_perf(tp, model_store)
