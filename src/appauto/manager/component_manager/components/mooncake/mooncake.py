from functools import cached_property
from appauto.manager.config_manager.config_logging import LoggingConfig
from appauto.manager.client_manager.linux import BaseLinux

logger = LoggingConfig.get_logger()


# TODO 后续是否需要提取 BaseLinux
# TODO 继承 BaseComponent -> Mooncake 没有 UI 也无需 curl URL, 也许不用通过 BaseComponent


class MoonCake(object):
    def __init__(self, mgt_ip, ssh_user="qujing", ssh_password="madsys123", ssh_port=22):
        self.mgt_ip = mgt_ip
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_port = ssh_port

        self.console = BaseLinux(self.mgt_ip, self.ssh_user, self.ssh_password, self.ssh_port)

    """
    1. check has_server, 如果有则跳过 start_server 直接 start_client
    2. start_server: mooncake_master -v=1 
    3. start_client( 可以起多个 )
    4. 尝试不同的 api
    """

    @property
    def has_server(self):
        rc, _, _ = self.console.run("ps aux | grep -v grep | grep mooncake_master; echo $?")
        return rc == 0

    def start_server(self):
        self.console.run("mooncake_master -v=1")

    def start_c(self):
        self.console.run("python3 start_client.py")

    def start_client(self):
        command = (
            f"export PROTOCOL={mc_store_setup_params.get('protocol', 'tcp')} && "
            f"export DEVICE_NAME={mc_store_setup_params.get('device_name', 'eno4')} && "
            f"export LOCAL_HOSTNAME={mc_store_setup_params.get('local_hostname', 'localhost')} && "
            f"export MC_METADATA_SERVER={mc_store_setup_params.get('metadata_server', 'http://127.0.0.1:8080/metadata')} && "
            f"export MASTER_SERVER={mc_store_setup_params.get('master_server', '127.0.0.1:50051')} && "
            f"python -c 'import your_module; your_module.start_client(mc_store)'"
        )
