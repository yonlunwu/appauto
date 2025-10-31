from typing import Literal
from functools import cached_property

from ..linux import BaseLinux
from .docker import BaseDockerTool


# Container 对象类
class BaseDockerContainer:
    def __init__(self, node: BaseLinux, name: str):
        self.node = node
        self.name = name
        self.docker_tool = BaseDockerTool(self.node)

    @cached_property
    def ctn_id(self) -> str:
        return self.docker_tool.get_ctn_id_by_name(self.name)

    def run(self, cmd: str, sudo=False, print_screen=False, timeout=None):
        full_cmd = f"docker exec {self.name} bash -c '{cmd}'"
        return self.node.run(full_cmd, sudo, False, False, print_screen, timeout)

    def run_in_thread(self, cmd: str, sudo=False): ...

    @property
    def is_running(self) -> Literal["yes", "no", "unknown"]:
        return self.docker_tool.is_running(self.ctn_id())

    def stop(self):
        self.docker_tool.stop_ctn(self.ctn_id)

        assert self.is_running == "no"

    def rm(self):
        self.docker_tool.rm_ctn(self.ctn_id)

    def restart(self):
        self.docker_tool.restart_ctn(self.ctn_id)

        assert self.is_running == "yes"

    def launch_model(self): ...
