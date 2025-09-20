"""
amaas 会统一提供一个 tar.gz
"""

from functools import partial
from concurrent.futures import wait
from typing import List, Union
from appauto.manager.config_manager.config_logging import LoggingConfig
from appauto.manager.utils_manager.custom_thread_pool_executor import (
    CustomThreadPoolExecutor,
    check_futures_exception,
    callback,
)

from ..base_deploy import BaseDeploy

logger = LoggingConfig.get_logger()


class DeployAmaaS(BaseDeploy):

    def __init__(self, amaas, ctn_names: Union[List, str] = None, deploy_path="/mnt/data/deploy/"):
        super().__init__(amaas, deploy_path)
        self.ctn_names = ctn_names or [
            "zhiwen-rag",
            "zhiwen-ames",
            "zhiwen-rag-web",
            "zhiwen-ames-web",
            "zhiwen-minio",
            "zhiwen-es",
            "zhiwen-redis",
            "zhiwen-mysql",
        ]

    def install(self, tar_name: str, force_load=True):
        folder = tar_name.split(".", 1)[0].split("-", 1)[-1]
        cmd = f"cd {self.deploy_path}{folder} && sudo bash install.sh {'-u' if force_load else ''}"
        self.amaas.cli.run_with_check(cmd, sudo=False)

    def _handle_old_ctns(self, ctn_names: List):

        self.prune("network")

        def _handle_old(ctn_name):
            if ctn_id := self.get_ctn_id_by_name(ctn_name):
                self.stop_ctn(ctn_id)
                self.rm_ctn(ctn_id)

        fus = []

        with CustomThreadPoolExecutor() as executor:
            for name in ctn_names:
                fu = executor.submit(_handle_old, name)
                fu.add_done_callback(partial(callback))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

    def _check_new_ctns(self, ctn_names: List):
        def _check_result(ctn_name):
            ctn_id = self.get_ctn_id_by_name(ctn_name)
            assert self.is_running(ctn_id) == "yes"

        fus = []

        with CustomThreadPoolExecutor() as executor:
            for name in ctn_names:
                fu = executor.submit(_check_result, name)
                fu.add_done_callback(partial(callback))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

    def deploy(self, tar_name: str, ctn_names: List = None, force_load=True):
        """
        ctn_names:
        - 要处理的容器名称列表.
        - 不传时默认为 self.ctn_names, 其默认值为:
            [
                "zhiwen-rag",
                "zhiwen-ames",
                "zhiwen-rag-web",
                "zhiwen-ames-web",
                "zhiwen-minio",
                "zhiwen-es",
                "zhiwen-redis",
                "zhiwen-mysql"
            ]

        force_load: 强制 load 镜像

        ### 步骤
            1. stop & 删除 old_ctn;
            2. rm old image;
            3. prune network;
            4. cd 指定路径, & 解压;
            5. cd 指定路径, & 执行 install.sh -u;
            6. docker ps 检查.
        """
        assert self.have_tar(tar_name) == "yes"

        ctn_names = ctn_names or self.ctn_names
        ctn_names = ctn_names if isinstance(ctn_names, list) else [ctn_names]

        # 旧包
        self._handle_old_ctns(ctn_names)

        # 新包
        self.decompress(tar_name)
        self.install(tar_name, force_load=force_load)
        self._check_new_ctns(ctn_names)
