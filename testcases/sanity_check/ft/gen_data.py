from pathlib import Path
from dataclasses import dataclass

import appauto
from appauto.operator.amaas_node import AMaaSNodeCli
from appauto.manager.config_manager import LoggingConfig
from appauto.manager.data_manager.gen_global_data import TEST_DATA_DICT

logger = LoggingConfig.get_logger()


_DEFAULT_IMAGE = str(Path(appauto.__file__).parent / "assets" / "ci_test.image")


@dataclass
class Defaultparams:
    ip: str = TEST_DATA_DICT.get("ip", None)
    ft_port: str = TEST_DATA_DICT.get("ft_port", None)
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
    vlm_image_path: str = TEST_DATA_DICT.get("vlm_image_path", _DEFAULT_IMAGE)
    model_priority = eval(TEST_DATA_DICT.get("model_priority", "['P0', 'P1']"))  # "None": 获取全部; "['P0']": 仅筛选 P0


assert Defaultparams.ip
assert Defaultparams.ft_port


amaas = AMaaSNodeCli(Defaultparams.ip, Defaultparams.ssh_user, ssh_port=Defaultparams.ssh_port)
ft_ctn = amaas.docker_ctn_factory.ft
