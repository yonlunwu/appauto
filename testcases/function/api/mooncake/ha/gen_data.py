from dataclasses import dataclass
from appauto.manager.component_manager.components.mooncake.mooncake import MoonCake
from appauto.manager.data_manager.gen_global_data import TEST_DATA_DICT


@dataclass
class DefaultParams:
    ip = TEST_DATA_DICT.get("mooncake_ip", "")
    client_count = TEST_DATA_DICT.get("client_count", 2)


mooncake = MoonCake(DefaultParams.ip)
