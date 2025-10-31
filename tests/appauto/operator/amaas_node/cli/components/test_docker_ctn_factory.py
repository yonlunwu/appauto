from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig


logger = LoggingConfig.get_logger()


amaas = AMaaSNode("192.168.110.4", ssh_user="qujing", skip_api=True)


class TestAMaasNodeDockerCtnFactory:
    def test_ft_container(self):
        ft_ctn = amaas.cli.docker_ctn_factory.ft
        ctn_id = ft_ctn.ctn_id
        logger.info(f"FT Container ID: {ctn_id}")
        assert ctn_id == "37c045745fcc"
