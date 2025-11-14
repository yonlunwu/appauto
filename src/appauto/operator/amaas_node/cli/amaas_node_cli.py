from functools import cached_property
from appauto.manager.client_manager import BaseLinux
from appauto.manager.utils_manager.format_output import remove_line_break

from .components.docker_ctn_factory import DockerContainerFactory


class AMaaSNodeCli(BaseLinux):
    def __init__(self, mgt_ip, ssh_user="qujing", ssh_password="madsys123", ssh_port=22):
        super().__init__(mgt_ip, ssh_user, ssh_password, ssh_port)
        self.docker_ctn_factory = DockerContainerFactory(self)

    def have_pid(self, pid: int) -> bool:
        cmd = f"docker exec zhiwen-ames ps -p {pid} "
        rc, _, _ = self.run(cmd)

        return not rc
