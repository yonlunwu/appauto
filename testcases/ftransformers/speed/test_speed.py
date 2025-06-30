import pytest
import allure
from datetime import datetime

from appauto.manager.connection_manager.local import Local
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


@allure.epic("TestSpeedEvalScope")
@pytest.mark.night
class TestSpeedEvalScope:
    def test_speed_demo(self):
        """使用 evalscope 测试 speed, 在被测主机上执行 swanlab watch 查看结果"""
        # TODO 明确需要测试哪些参数组合, 提供的参数可以看 cli
        # TODO 当前 sglang 引擎那边 usage 没有需要的信息, 最好是引擎侧修改一下
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"appauto-bench-{timestamp}"
        cmd = (
            "appauto bench evalscope perf --mgt-ip 192.168.110.15 --port 11002 "
            " --parallel 1 2 4 8 "
            " --number 4 4 4 4 "
            " --model DeepSeek-R1-GPTQ4-experts "
            " --tokenizer-path DeepSeek-R1-GPTQ4-experts "
            f" --name {name}"
        )

        Local.run(cmd)
        logger.info(f" please run cmd: swanlab watch ./outputs -h 0.0.0.0 and check result {name}".center(200, "="))
