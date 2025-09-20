from functools import cached_property
from appauto.manager.client_manager import BaseLinux
from appauto.manager.utils_manager.format_output import remove_line_break


class AMaaSNodeCli(BaseLinux):
    def __init__(self, mgt_ip, ssh_user="qujing", ssh_password="madsys123", ssh_port=22):
        super().__init__(mgt_ip, ssh_user, ssh_password, ssh_port)

    @cached_property
    def nic_mac_addr(self) -> str:
        cmd = (
            'ip link show | awk \'/^[0-9]+: / { dev = $2; sub(/:/, "", dev); next; } '
            "/link\/ether/ && dev !~ /^(lo|docker|veth)/ { print toupper($2); exit; }'"
        )
        _, res, _ = self.run(cmd)

        return remove_line_break(res)
