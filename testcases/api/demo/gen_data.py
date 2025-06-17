from dataclasses import dataclass
from appauto.manager.component_manager.components.kllm.kllm import Kllm
from appauto.manager.config_manager import LoggingConfig
from appauto.manager.data_manager.gen_global_data import TEST_DATA_DICT


logger = LoggingConfig.get_logger()


@dataclass
class DefaultParams:
    ip: str = TEST_DATA_DICT.get("kllm_ip", "")
    port: str = TEST_DATA_DICT.get("kllm_port", "")


assert DefaultParams.ip


KLLM = Kllm(DefaultParams.ip, DefaultParams.port)
