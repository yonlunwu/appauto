from dataclasses import dataclass

from appauto.operator import AMaaSNode
from appauto.manager.config_manager import LoggingConfig
from appauto.manager.data_manager.gen_global_data import TEST_DATA_DICT


logger = LoggingConfig.get_logger()


@dataclass
class DefaultParams:
    ip: str = TEST_DATA_DICT.get("ip", "192.168.111.11")
    port: str = TEST_DATA_DICT.get("amaas_port", "10001")
    ssh_user: str = TEST_DATA_DICT.get("ssh_user", "zkyd")
    ssh_port: str = TEST_DATA_DICT.get("ssh_port", 22)
    tp = eval(TEST_DATA_DICT.get("tp", "[1, 2, 4, 8]"))
    llm_questions = [
        "35+25+10=60，对吗？",
        "天空为什么是蓝色的？",
        "Wish you happiness each day and all the best in everything",
        "用python写冒泡排序的代码，关键处请添加注释",
        "写愤怒的小鸟的代码",
        "请给我一份周末北京旅游攻略，去什么景点吃什么走什么路线有什么注意事项都写的详细一些",
    ]
    model_priority = eval(TEST_DATA_DICT.get("model_priority", "['P0', 'P1']"))  # "None": 获取全部; "['P0']": 仅筛选 P0


assert DefaultParams.ip


amaas = AMaaSNode(
    DefaultParams.ip, ssh_user=DefaultParams.ssh_user, ssh_port=DefaultParams.ssh_port, api_port=DefaultParams.port
)
