from time import sleep
from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig


logger = LoggingConfig.get_logger()


amaas = AMaaSNode("192.168.111.10", ssh_user="qujing", skip_api=True)
# amaas = AMaaSNode("115.120.24.105", ssh_user="root", skip_api=True, ssh_password="5F0.RRGlruoR1Lp8D5q6EmvesR")


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

    def test_ft_launch_model_and_run_eval(self):
        ft_ctn = amaas.cli.docker_ctn_factory.ft
        # model = "GLM-4.5-GPU-weight"
        model = "DeepSeek-R1-0528-GPU-weight"
        port = 30012

        # 拉模型
        ft_ctn.launch_model_in_thread(model, tp=1, mode="correct", port=port, wait_for_running=True)

        sleep(5)

        # 获取模型 pid
        pids = ft_ctn.get_running_model_pids(ft_ctn.engine, model)
        logger.info(pids)
        assert pids

        sleep(5)

        # 跑 evalscope
        ft_ctn.run_eval_via_evalscope(port, model, "aime24", concurrency=4, limit=4)

        # 停模型
        ft_ctn.stop_model(model)

        pids = ft_ctn.get_running_model_pids(ft_ctn.engine, model)
        logger.info(pids)
        assert not pids

    def test_ft_launch_model_and_run_perf(self):
        ft_ctn = amaas.cli.docker_ctn_factory.ft
        model = "DeepSeek-R1-0528-GPU-weight"
        port = 30013

        # 拉模型
        ft_ctn.launch_model_in_thread(model, 2, "perf", port, wait_for_running=True)

        sleep(5)

        # 获取模型 pid
        pids = ft_ctn.get_running_model_pids(ft_ctn.engine, model)
        logger.info(pids)
        assert pids

        sleep(5)

        # 跑 evalscope
        ft_ctn.run_perf_via_evalscope(port, model, "1 4", "1 4", 128, 512)

        # 停模型
        ft_ctn.stop_model(model)

        pids = ft_ctn.get_running_model_pids(ft_ctn.engine, model)
        logger.info(pids)
        assert not pids

    def test_ft_launch_model_huawei(self):
        ft_ctn = amaas.cli.docker_ctn_factory.ft
        model = "DeepSeek-R1-0528-AWQ-GPU-weight"
        tp = 8
        port = 30000

        # as_correct
        ft_ctn.launch_model_in_thread(model, tp, "correct", port)

        # # as_perf
        # ft_ctn.launch_model_in_thread(model, tp, "perf", port)
