from .ft import FTModelParams
from .amaas import AMaaSModelParams
from typing import Literal
from ....manager.client_manager import BaseLinux
from ....manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


class ModelParamsConstrutor:
    def __init__(
        self,
        node: BaseLinux,
        engine: Literal["sglang", "ft"] = None,
        model_name: str = None,
        tp: Literal[1, 2, 4, 8] = None,
        mode: Literal["correct", "perf", "mtp_correct", "mtp_perf"] = "correct",
        port: int = 30000,
    ):
        self.ft = FTModelParams(node, engine, model_name, tp, mode, port)
        self.amaas = AMaaSModelParams(model_name, tp)
