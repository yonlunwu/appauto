from time import time, sleep

from appauto.manager.component_manager.components.amaas.models.model_store import ModelStore
from appauto.manager.config_manager import LoggingConfig

from testcases.amaas.gen_data import amaas, DefaultParams as DP

logger = LoggingConfig.get_logger()


class CommonStepModelAction:
    @classmethod
    def choose_model_store(cls): ...

    @classmethod
    def wait_model_running(cls, timeout_s: int = DP.wait_model_running_timeout_s):
        start_time = time()
        failed_models = []

        model = None

        while time() - start_time <= timeout_s:
            model = amaas.models[0]
            if model.status == "running":
                break
            elif model.status == "error":
                failed_models.append(model.name)
                model.stop()
                break

            sleep(10)

        return model

    @classmethod
    def check_and_run_model(cls, model_store: ModelStore, gpu_num: int = None):
        rule = model_store.get_run_rule()
        model_store.check(access_limit=rule.data.access_limit, max_token=rule.data.max_total_tokens)
        model_store.run(access_limit=rule.data.access_limit, max_token=rule.data.max_total_tokens)


class CommonRunTestAMaaSAPI:
    @classmethod
    def run_llm_test(cls, gpu_num: int = None):
        llm_model_stores = [model for model in amaas.llm_model_stores if model.source == "init"]

        for m_s in llm_model_stores:
            CommonStepModelAction.check_and_run_model(m_s, gpu_num)
            model = CommonStepModelAction.wait_model_running()

            assert model

            # TODO filter correct chat
            chat = amaas.llm_chats[0]
            chat.talk()
            res = chat.talk("test", process_stream=False)
            logger.info(f"得到了回复: {res}")

            model.stop()

    @classmethod
    def run_vlm_test(cls):
        ...
        # for
        # check & run
        # wait running
        # 多模态
        # 合理的 check


class CommonCheckAMaaSAPI:
    @classmethod
    def check_aaa(cls): ...
