from typing import Literal
from functools import cached_property
from appauto.manager.client_manager import BaseLinux
from appauto.manager.utils_manager.format_output import remove_line_break

from .components.docker import AMaaSDocker


class AMaaSNodeCli(BaseLinux):
    def __init__(self, mgt_ip, ssh_user="qujing", ssh_password="madsys123", ssh_port=22):
        self.docker = AMaaSDocker(mgt_ip, ssh_user, ssh_password, ssh_port)
        super().__init__(mgt_ip, ssh_user, ssh_password, ssh_port)

    @cached_property
    def nic_mac_addr(self) -> str:
        cmd = (
            'ip link show | awk \'/^[0-9]+: / { dev = $2; sub(/:/, "", dev); next; } '
            "/link\/ether/ && dev !~ /^(lo|docker|veth)/ { print toupper($2); exit; }'"
        )
        _, res, _ = self.run(cmd)

        return remove_line_break(res)

    def have_pid(self, pid: int) -> bool:
        cmd = f"docker exec zhiwen-ames ps -p {pid} "
        rc, _, _ = self.run(cmd)

        return not rc

    def run_as_perf(
        self,
        model_name,
        tp: Literal[1, 2, 4, 8],
        dp: int = 2,
    ):
        """
        以性能测试参数拉起模型
        """
        ...
