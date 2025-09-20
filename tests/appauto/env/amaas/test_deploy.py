from appauto.env.amaas.deploy import DeployAmaaS
from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig


logger = LoggingConfig.get_logger()

# # zkyd45
# amaas = AMaaSNode("120.211.1.45", ssh_user="zkyd", skip_api=True)
# # zkyd46
# amaas = AMaaSNode("120.211.1.46", ssh_user="zkyd", skip_api=True)
# zkyd55
amaas = AMaaSNode("120.211.1.55", ssh_user="zkyd", skip_api=True)
# # autotest
# amaas = AMaaSNode("192.168.111.10", ssh_user="qujing", skip_api=True)
# # sa4
# amaas = AMaaSNode("117.133.60.232", ssh_user="qujing", skip_api=True)


deploy = DeployAmaaS(amaas)


class TestDeployAmaaS:

    def test_get_ctn_names_ids_map(self):
        res = deploy.get_ctn_names_ids_map()
        {
            "zhiwen-rag-web": "7924f666d41c",
            "zhiwen-ames-web": "07fe745e8e8c",
            "zhiwen-rag": "3016652db04e",
            "zhiwen-ames": "cd5a75869205",
            "zhiwen-minio": "13c15071349e",
            "zhiwen-es": "a6417a67a547",
            "zhiwen-redis": "cf0604377f2f",
            "zhiwen-mysql": "0e67d73b1b50",
        }
        logger.info(res)

    def test_deploy_amaas(self):
        deploy.deploy(tar_name="zhiwen-20250918_1307.tar.gz")

    def test_run_cmd(self):
        from appauto.manager.utils_manager.custom_thread_pool_executor import (
            CustomThreadPoolExecutor,
            callback,
            check_futures_exception,
        )
        from functools import partial
        from concurrent.futures import wait

        fus = []
        with CustomThreadPoolExecutor() as executor:
            for _ in range(10):
                fu = executor.submit(amaas.cli.run, "date")
                fu.add_done_callback(partial(callback))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)
