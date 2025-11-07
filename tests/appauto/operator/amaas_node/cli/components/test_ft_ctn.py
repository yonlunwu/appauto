import threading
from time import sleep
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

    def test_ft_launch_model(self):
        ft_ctn = amaas.cli.docker_ctn_factory.ft
        ft_ctn.launch_model("DeepSeek-V3-0324-GPU-weight", tp=2, mode="correct", port=30011)

        # 获取模型 pid
        pids = ft_ctn.get_running_model_pids(ft_ctn.engine, "DeepSeek-V3-0324-GPU-weight")
        logger.info(pids)
        assert pids

        sleep(5)

        # 停模型
        ft_ctn.stop_model("DeepSeek-V3-0324-GPU-weight")

        pids = ft_ctn.get_running_model_pids(ft_ctn.engine, "DeepSeek-V3-0324-GPU-weight")
        logger.info(pids)
        assert not pids

    def test_ft_launch_model_in_thread(self):
        ft_ctn = amaas.cli.docker_ctn_factory.ft

        # 拉模型
        ft_ctn.launch_model_in_thread(
            "DeepSeek-V3-0324-GPU-weight", tp=2, mode="correct", port=30012, wait_for_running=True
        )

        sleep(5)

        # 获取模型 pid
        pids = ft_ctn.get_running_model_pids(ft_ctn.engine, "DeepSeek-V3-0324-GPU-weight")
        logger.info(pids)
        assert pids

        sleep(5)

        # 停模型
        ft_ctn.stop_model("DeepSeek-V3-0324-GPU-weight")

        pids = ft_ctn.get_running_model_pids(ft_ctn.engine, "DeepSeek-V3-0324-GPU-weight")
        logger.info(pids)
        assert not pids
