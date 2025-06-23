from dataclasses import dataclass
from appauto.manager.component_manager.components.engine.sglang import SGLang
from appauto.manager.server_manager import SGLangServer
from appauto.manager.config_manager import LoggingConfig
from appauto.manager.data_manager.gen_global_data import TEST_DATA_DICT


logger = LoggingConfig.get_logger()


@dataclass
class DefaultParams:
    ip: str = TEST_DATA_DICT.get("sglang_ip", "192.168.110.15")
    port: str = TEST_DATA_DICT.get("sglang_port", 11002)


assert DefaultParams.ip


sglang = SGLang(DefaultParams.ip, DefaultParams.port)
# TODO 先写死
sglang_server = SGLangServer(
    mgt_ip="192.168.110.15",
    conda_path="/home/zkyd/miniconda3/bin/conda",
    conda_env_name="yanlong-ft",
    model_path="DeepSeek-R1-GPTQ4-experts",
    amx_weight_path="DeepSeek-R1-INT4",
    served_model_name="DeepSeek-R1",
    cpuinfer=80,
    ssh_user="zkyd",
    ssh_password="zkyd@12#$",
)
