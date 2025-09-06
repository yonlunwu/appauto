from typing import List
from dataclasses import dataclass
from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig
from appauto.manager.data_manager.gen_global_data import TEST_DATA_DICT


logger = LoggingConfig.get_logger()


@dataclass
class DefaultParams:
    ip: str = TEST_DATA_DICT.get("amaas_ip", "117.133.60.227")
    port: str = TEST_DATA_DICT.get("amaas_port", "10001")
    init_model_store_type = eval(
        TEST_DATA_DICT.get("init_model_store_type", '["llm", "vlm", "embedding", "rerank", "parser", "audio"]')
    )
    wait_model_running_timeout_s: int = int(TEST_DATA_DICT.get("wait_model_running_timeout_s", 600))
    concurrency: int = int(TEST_DATA_DICT.get("concurrency", 2))
    query_count: int = int(TEST_DATA_DICT.get("query_count", 4))
    model_name: str = TEST_DATA_DICT.get("model_name", "Qwen2.5-7B-Instruct")


assert DefaultParams.ip
# assert DefaultParams.name


amaas = AMaaS(DefaultParams.ip, DefaultParams.port)
