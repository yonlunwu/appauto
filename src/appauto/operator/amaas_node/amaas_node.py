from .amaas_node_api import AMaaSNodeApi
from .cli.amaas_node_cli import AMaaSNodeCli


class AMaaSNode:
    def __init__(
        self,
        mgt_ip=None,
        ssh_user="qujing",
        ssh_passwd="madsys123",
        ssh_port=22,
        api_port=10001,
        api_user="admin",
        api_passwd="123456",
        object_id=None,
        data=None,
        ssl_enabled=False,
        parent_tokens=None,
        skip_api=False,
        skip_cli=False,
    ):

        self.api = (
            AMaaSNodeApi(mgt_ip, api_port, api_user, api_passwd, object_id, data, ssl_enabled, parent_tokens)
            if not skip_api
            else None
        )
        self.cli = AMaaSNodeCli(mgt_ip, ssh_user, ssh_passwd, ssh_port) if not skip_cli else None
