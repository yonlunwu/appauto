from appauto.env.ftransformers.deploy import DeployFT
from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig


logger = LoggingConfig.get_logger()

# zkyd45
amaas = AMaaSNode("120.211.1.45", ssh_user="zkyd", skip_api=True)
# # zkyd46
# amaas = AMaaSNode("120.211.1.46", ssh_user="zkyd", skip_api=True)
# # zkyd55
# amaas = AMaaSNode("120.211.1.55", ssh_user="zkyd", skip_api=True)
# # autotest
# amaas = AMaaSNode("192.168.111.10", ssh_user="qujing", skip_api=True)
# # sa4
# amaas = AMaaSNode("117.133.60.232", ssh_user="qujing", skip_api=True)


deploy = DeployFT(amaas)


class TestDeployFT:
    def test_is_running(self):
        ctn_id = deploy.get_ctn_id_by_name(ctn_name=deploy.ctn_names)
        assert deploy.is_running(ctn_id) == "yes"

    def test_gen_docker_compose(self):
        docker_compose = deploy.gen_docker_compose(tag="v3.3.0-test5")
        amaas.cli.upload(f"/mnt/data/deploy/{docker_compose}", local_path=docker_compose)

    def test_have_image(self):
        assert deploy.have_tar("zhiwen-ftransformers-v3.3.0-test2.tar") == "no"
        assert deploy.have_tar("zhiwen-ftransformers-v3.3.0-test4.tar") == "yes"

    def test_get_ctn_id_by_name(cls):
        res = deploy.get_ctn_id_by_name("zhiwen-ft")
        logger.info(res)

        assert res == "93e8feef6848"

    def test_stop_ctn(self):
        ctn_id = deploy.get_ctn_id_by_name(ctn_name="zhiwen-ft")
        deploy.stop_ctn(ctn_id)

        assert deploy.is_running(ctn_id) == "no"

    def test_deploy_ft(self):
        deploy.deploy(tar_name="zhiwen-ftransformers-v3.3.0-test4.tar", tag="v3.3.0-test4", stop_old=True)
