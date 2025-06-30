import pytest
import allure
from time import time
from typing import Tuple

from appauto.manager.config_manager import LoggingConfig
from testcases.ftransformers.gen_data import sglang, sglang_server

logger = LoggingConfig.get_logger()


class CommonSpeed:
    @allure.step("measure_speed")
    def measure_speed(self, prompt, max_tokens) -> Tuple[float, float]:
        # TODO 除了 ttft 还需要 prefill_speed 和 decode_speed
        start_time = time()
        ttft = sglang.talk(
            prompt,
            sglang_server.served_model_name,
            stream=True,
            temperature=0.6,
            top_p=1.0,
            max_tokens=max_tokens,
            measure_ttft=True,
        )
        elapse = time() - start_time

        return ttft, elapse


class CommonRunTestSpeed: ...
