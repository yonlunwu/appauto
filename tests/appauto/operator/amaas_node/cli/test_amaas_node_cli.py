from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()

amaas = AMaaSNode("192.168.110.4", ssh_user="qujing", skip_api=True)


class TestAMaaSNodeCli:

    def test_nic_mac_addr(self):
        logger.info(amaas.cli.nic_mac_addr)
        assert amaas.cli.nic_mac_addr == "18:9B:A5:84:D4:80"

    def test_docker_ctn_factory(self):
        ctn_id = amaas.cli.docker_ctn_factory.ft.ctn_id
        logger.info(ctn_id)
        assert ctn_id == "37c045745fcc"

    def test_collect_local_models(self):
        res = amaas.cli.local_models()
        logger.info(res)
