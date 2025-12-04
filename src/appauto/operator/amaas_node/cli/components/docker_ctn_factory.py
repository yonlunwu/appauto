from typing import TYPE_CHECKING
from functools import cached_property
from appauto.manager.config_manager.config_logging import LoggingConfig
from .ft_ctn import FTContainer

if TYPE_CHECKING:
    from ..amaas_node_cli import AMaaSNodeCli

logger = LoggingConfig.get_logger()


class DockerContainerFactory:
    def __init__(self, node: "AMaaSNodeCli"):
        self.node = node

    # 基于 ft 做测试，name 就是 zhiwen-ft
    @cached_property
    def ft(self) -> FTContainer:
        name, engine = "", ""

        if self.node.gpu_type == "nvidia":
            name = "zhiwen-ft"
            engine = "ftransformers"
        elif self.node.gpu_type == "huawei":
            name = "zhiwen-ft-ascend"
            engine = "sglang"

        assert engine

        return FTContainer(self.node, name=name, engine=engine)

    # # 基于 ames 做测试，name 是 instance_name
    # def amaas_model_instance(self, ins_name: str) -> BaseDockerContainer:
    #     return BaseDockerContainer(self.node, name=ins_name)
