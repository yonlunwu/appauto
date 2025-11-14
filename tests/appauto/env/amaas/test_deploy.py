from appauto.env import DeployAmaaS
from appauto.manager.config_manager.config_logging import LoggingConfig


logger = LoggingConfig.get_logger()

# # zkyd45
# amaas = AMaaSNode("120.211.1.45", ssh_user="zkyd", skip_api=True)
# # zkyd46
# amaas = AMaaSNode("120.211.1.46", ssh_user="zkyd", skip_api=True)
# # zkyd55
# amaas = AMaaSNode("120.211.1.55", ssh_user="zkyd", skip_api=True)
# # qu1
# amaas = AMaaSNode("192.168.111.10", ssh_user="qujing", skip_api=True)
# # qu4
# amaas = AMaaSNode("192.168.110.4", ssh_user="qujing", skip_api=True)


deploy = DeployAmaaS("192.168.110.4", "qujing")


class TestDeployAmaaS:

    def test_deploy_amaas(self):
        deploy.deploy("zhiwen-20251111_2107.tar.gz", "v3.3.1")

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
                fu = executor.submit(deploy.run, "date")
                fu.add_done_callback(partial(callback))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)
