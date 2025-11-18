"""
Module for constructing model parameters.
    1. 根据 model 获取 model.yaml
    2. load_yaml 并根据 tp 和 mode 获取对应的启动命令
"""

from typing import Literal
from functools import cached_property
from ....manager.file_manager.handle_yml import YMLHandler
from ....manager.client_manager import BaseLinux
from ....manager.config_manager.config_logging import LoggingConfig
from ....manager.error_manager.errors import OperationNotSupported

logger = LoggingConfig.get_logger()


class FTModelParams:
    # TODO 支持更多 engine
    def __init__(
        self,
        node: BaseLinux,
        engine: Literal["sglang", "ft"],
        model_name: str,
        tp: int,
        mode: Literal["correct", "perf", "mtp_correct", "mtp_perf"] = "correct",
        port: int = 30000,
    ):
        """
        - correct: 即 default, sanity_check 和 正确性测试模式;
        - perf: 性能测试模式;
        - mtp_correct: 开启 mtp 的正确性测试模式;
        - mtp_perf: 开启 mtp 的性能测试模式;
        """
        self.node = node
        self.engine = engine
        self.model_name = model_name
        self.tp = tp
        self.mode = mode
        self.port = port

    @cached_property
    def prefix(self):
        # TODO  根据 engine 返回对应前缀
        if self.engine == "sglang":
            from ...model_params.common import SGLANG_PREFIX

            return SGLANG_PREFIX.format(self.port) + " "
        elif self.engine == "ft":
            from ...model_params.common import FT_PREFIX

            return FT_PREFIX.format(self.port) + " "

        return ""

    @cached_property
    def gpu_type(self) -> str:
        # TODO 根据 self.node 获取实际 GPU 类型
        return "nvidia"

    @cached_property
    def model_type(self) -> str:
        # TODO 根据 self.model_name 获取实际模型类型
        return "llm"

    @cached_property
    def model_family(self) -> Literal["deepseek", "qwen", "glm", "kimi"]:
        if self.model_name.startswith("DeepSeek"):
            return "deepseek"
        elif self.model_name.startswith("GLM"):
            return "glm"
        elif self.model_name.startswith("Qwen"):
            return "qwen"
        elif self.model_name.startswith("Kimi"):
            return "kimi"

    @cached_property
    def handler(self) -> YMLHandler:
        # 根据 model_name, tp, mode 返回对应的 yaml 路径
        # TODO 1. 根据 self.node 获取卡类型
        yml_path = f"src/appauto/organizer/model_params/{self.gpu_type}/{self.model_type}/{self.model_family}/{self.model_name}.yaml"
        return YMLHandler(yml_path)

    @cached_property
    def as_cmd(self):
        """
        根据 tp 和 mode 生成最终的命令行参数字符串
        规则: common + dynamic + (perf_common + perf) 或者 (correct_common + correct)

        如果模型 yml 中没有声明 perf, 则 perf 直接采用 correct 即可.
        """
        yml_data = self.handler.data.engine
        common = yml_data.common
        dynamic = yml_data.dynamic

        mode_common, mode_spec = {}, {}

        # TODO 补全更多 mode 以及考虑当不存在指定 mode 时的处理
        if self.mode == "perf":
            mode_common = yml_data.perf_common or yml_data.correct_common or {}
            mode_spec = yml_data.perf.get(self.tp, {}) or yml_data.correct.get(self.tp, {})
        elif self.mode == "correct":
            mode_common = yml_data.correct_common or {}
            mode_spec = yml_data.correct.get(self.tp, {})

        # 存在指定的 tp 说明支持该 tp, 否则说明是不支持的
        # 如果支持该 tp 则进行 cmd 合并拼接
        if mode_spec:

            final_params = {**common, **dynamic, **mode_common, **mode_spec}

            # 生成命令行参数字符串
            cmd_parts = []
            for key, value in final_params.items():
                if isinstance(value, bool):
                    if value:
                        cmd_parts.append(f"--{key}")
                else:
                    cmd_parts.append(f"--{key} {value}")

            cmd_str = " ".join(cmd_parts)
            return self.prefix + cmd_str

        raise OperationNotSupported(f"{self.model_name} doesn't support tp {self.tp}, mode: {self.mode}")
