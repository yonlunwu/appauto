# from appauto.env.ftransformers.deploy import DeployFT
from appauto.env import DeployFT
from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig


logger = LoggingConfig.get_logger()

# # zkyd45
# amaas = AMaaSNode("192.168.111.11", ssh_user="zkyd", skip_api=True)
# # zkyd46
# amaas = AMaaSNode("192.168.111.19", ssh_user="zkyd", skip_api=True)
# # zkyd55
# amaas = AMaaSNode("192.168.111.18", ssh_user="zkyd", skip_api=True)
# # qu1
# amaas = AMaaSNode("192.168.111.10", ssh_user="qujing", skip_api=True)
# # qu4
# amaas = AMaaSNode("192.168.110.4", ssh_user="qujing", skip_api=True)


# deploy = DeployFT(amaas)
deploy = DeployFT("192.168.111.19", "zkyd")


class TestDeployFT:
    def test_is_running(self):
        ctn_id = deploy.docker_tool.get_ctn_id_by_name(ctn_name=deploy.ctn_names)
        assert deploy.docker_tool.is_running(ctn_id) == "yes"

    def test_deploy_ft(self):
        deploy.deploy("zhiwen-ftransformers-3.3.2rc1.post1.tar", tag="3.3.2rc1.post1")
