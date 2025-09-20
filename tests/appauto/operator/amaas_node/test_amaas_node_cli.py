from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()

amaas = AMaaSNode("120.211.1.46", ssh_user="zkyd", skip_api=True)


class TestAMaaSNodeCli:

    def test_nic_mac_addr(self):
        logger.info(amaas.cli.nic_mac_addr)
        assert amaas.cli.nic_mac_addr == "18:9B:A5:84:D4:80"
