from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()

amaas = AMaaSNode("120.211.1.45", ssh_user="zkyd", skip_api=True)


class TestAMaasNodeDocker:
    def test_restart_zhiwen_ames(self):
        ctn_id = amaas.cli.docker_tool.get_ctn_id_by_name("zhiwen-ames")
        amaas.cli.docker_tool.restart_ctn(ctn_id)
