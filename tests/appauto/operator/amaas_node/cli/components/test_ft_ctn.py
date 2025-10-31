from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig


logger = LoggingConfig.get_logger()


amaas = AMaaSNode("192.168.110.4", ssh_user="qujing", skip_api=True)


class TestAMaasNodeFtContainer:
    def test_ft_container(self):
        ft_ctn = amaas.cli.docker_ctn_factory.ft
        ctn_id = ft_ctn.ctn_id
        logger.info(f"FT Container ID: {ctn_id}")
        assert ctn_id == "37c045745fcc"

    # TODO 这里需要放在线程中
    def test_ft_launch_model(self):
        ft_ctn = amaas.cli.docker_ctn_factory.ft
        rc, out, err = ft_ctn.launch_model("DeepSeek-V3-0324-GPU-weight", tp=2, mode="correct")
        logger.info(f"Launch model rc: {rc}, out: {out}, err: {err}")
        assert rc == 0
