from dataclasses import dataclass
from appauto.manager.component_manager.components.amaas import AMaaS
from appauto.manager.config_manager import LoggingConfig
from appauto.manager.data_manager.gen_global_data import TEST_DATA_DICT


logger = LoggingConfig.get_logger()


@dataclass
class DefaultParams:
    ip: str = TEST_DATA_DICT.get("amaas_ip", "117.133.60.227")
    port: str = TEST_DATA_DICT.get("amaas_port", "10001")
    tp = eval(TEST_DATA_DICT.get("tp", "[1, 2, 4, 8]"))
    wait_model_running_timeout_s: int = int(TEST_DATA_DICT.get("wait_model_running_timeout_s", 900))
    concurrency: int = int(TEST_DATA_DICT.get("concurrency", 2))
    query_count: int = int(TEST_DATA_DICT.get("query_count", 4))
    prompt_length: int = int(TEST_DATA_DICT.get("prompt_length", 128))
    model_name: str = TEST_DATA_DICT.get("model_name", "Qwen2.5-7B-Instruct")
    max_nb_chars: int = int(TEST_DATA_DICT.get("max_nb_chars", "512"))
    scene_loop: int = int(TEST_DATA_DICT.get("scene_loop", "3"))


assert DefaultParams.ip


amaas = AMaaS(DefaultParams.ip, DefaultParams.port)
