"""
amaas 会统一提供一个 tar.gz
"""

from functools import partial
from concurrent.futures import wait
from typing import List, Union, Literal
from appauto.manager.utils_manager.format_output import str_to_list_by_split
from appauto.manager.utils_manager.custom_thread_pool_executor import (
    CustomThreadPoolExecutor,
    check_futures_exception,
    callback,
)
from appauto.manager.config_manager.config_logging import LoggingConfig
from appauto.manager.utils_manager.custom_thread_pool_executor import (
    CustomThreadPoolExecutor,
    check_futures_exception,
    callback,
)


from ..base_deploy import BaseDeploy


logger = LoggingConfig.get_logger()


DEFAULT_CTN_NAMES = [
    "zhiwen-rag",
    "zhiwen-ames",
    "zhiwen-rag-web",
    "zhiwen-ames-web",
    "zhiwen-minio",
    "zhiwen-es",
    "zhiwen-redis",
    "zhiwen-mysql",
]

DEFAULT_IMAGE_NAMES = [
    "zhiwen-ames",
    "zhiwen-rag",
    "zhiwen-ames-web",
    "zhiwen-rag-web",
    "zhiwen-ftransformers",
    "zhiwen-transformers",
    "zhiwen-llama-box",
    "zhiwen-parser",
    "zhiwen-vox-box",
    "zhiwen-ktransformers",
    "zhiwen-vllm",
    "zhiwen-redis",
    "zhiwen-minio",
    "zhiwen-mysql",
    "zhiwen-es",
]

DEFAULT_THIRD_PARTY = {
    "zhiwen-redis": "7.2.4",
    "zhiwen-minio": "RELEASE.2023-12-20T01-00-02Z",
    "zhiwen-mysql": "8.0.35",
    "zhiwen-es": "8.11.3",
    "zhiwen-ktransformers": "3.2.2",
}


class DeployAmaaS(BaseDeploy):
    def __init__(
        self,
        mgt_ip,
        ssh_user="qujing",
        ssh_password="madsys123",
        ssh_port=22,
        deploy_path="/mnt/data/deploy/",
        ctn_names: Union[List, str] = None,
        image_names: Union[List, str] = None,
    ):
        super().__init__(mgt_ip, ssh_user, ssh_password, ssh_port, deploy_path)
        self.ctn_names = ctn_names or DEFAULT_CTN_NAMES
        self.image_names = image_names or DEFAULT_IMAGE_NAMES

    def _handle_old_ctns(self, ctn_names: List):

        def _handle_old(ctn_name):
            if ctn_id := self.docker_tool.get_ctn_id_by_name(ctn_name):
                self.docker_tool.stop_ctn(ctn_id)
                self.docker_tool.rm_ctn(ctn_id)

        fus = []

        with CustomThreadPoolExecutor() as executor:
            for name in ctn_names:
                fu = executor.submit(_handle_old, name)
                fu.add_done_callback(partial(callback))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

        self.docker_tool.prune("network")

    def _handle_old_images(self, tag: str, image_names: List = None):
        """
        比直接根据 image_id 删除精准,  tag 就是当前版本的 tag.
        """
        image_names = image_names or self.image_names
        image_names = image_names if isinstance(image_names, List) else [image_names]

        def _get_tag_for_spec_image(image_name):

            return DEFAULT_THIRD_PARTY.get(image_name, None)

        fus = []
        with CustomThreadPoolExecutor() as executor:
            for i_name in self.image_names:
                _tag = _get_tag_for_spec_image(i_name) or tag
                fu = executor.submit(self.docker_tool.rm_image_by_tag, i_name, _tag, True)
                fu.add_done_callback(partial(callback))
                fus.append(fu)

            wait(fus)

        self.docker_tool.prune("image")

        check_futures_exception(fus)

    def _collect_images_id(self) -> List[str]:
        cmd = (
            'docker image ls -q --filter "reference=zhiwen-*" | xargs -I {} docker image inspect '
            "--format '{{.RepoTags}} {{.ID}}' {} | awk '!index($1, \"post\") {print substr($2, 8, 12)}'"
        )
        _, res, _ = self.run(cmd)
        return str_to_list_by_split(res)

    # def _handle_old_images(self):
    #     images_id = self._collect_images_id()

    #     fus = []
    #     with CustomThreadPoolExecutor() as executor:
    #         for i_id in images_id:
    #             fu = executor.submit(self.docker_tool.rm_image_by_id, i_id, True)
    #             fu.add_done_callback(partial(callback))
    #             fus.append(fu)

    #         wait(fus)

    #     check_futures_exception(fus)

    def install(self, tar_name: str, force_load=True):
        folder = tar_name.split(".", 1)[0].split("-", 1)[-1]
        cmd = f"cd {self.deploy_path}{folder} && sudo bash install.sh {'-u' if force_load else ''}"
        self.run_with_check(cmd, sudo=False)

    def check_new_ctns(self, ctn_names: List):
        def _check_result(ctn_name):
            ctn_id = self.docker_tool.get_ctn_id_by_name(ctn_name)
            assert self.docker_tool.is_running(ctn_id) == "yes"

        fus = []

        with CustomThreadPoolExecutor() as executor:
            for name in ctn_names:
                fu = executor.submit(_check_result, name)
                fu.add_done_callback(partial(callback))
                fus.append(fu)

            wait(fus)

        check_futures_exception(fus)

    def deploy(self, tar_name: str, tag: str, ctn_names: List = None, force_load=True) -> Literal["succeed", "failed"]:
        """
        - tag: 目标 tag, 比如 v3.3.1

        - ctn_names:
            - 要处理的容器名称列表, 不传时默认为 self.ctn_names, 其默认值为:
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

        - force_load: 强制 load 镜像

        ### 步骤
            1. stop & delete old ctns;
            2. rm old images;
            3. prune network;
            4. cd 指定路径, & 解压;
            5. cd 指定路径, & 执行 install.sh -u;
            6. docker ps 检查新容器.
        """

        try:
            assert self.have_tar(tar_name) == "yes", f"The {tar_name} doesn't exist."

            ctn_names = ctn_names or self.ctn_names
            ctn_names = ctn_names if isinstance(ctn_names, list) else [ctn_names]

            # TODO 上面也许有运行中的模型，是否需要全干掉？

            #  删除旧容器
            self._handle_old_ctns(ctn_names)

            # 删除旧镜像
            self._handle_old_images(tag)

            # 删除旧 network
            self.docker_tool.prune("network")

            # TODO 删除 AMES 目录(影响 license)

            # 新包
            self.decompress(tar_name)
            self.install(tar_name, force_load)
            self.check_new_ctns(ctn_names)

            # TODO 上传 license
            logger.info("deploying amaas succeed.")
            return "succeed"

        except Exception as e:
            logger.error(f"error occurred while deploying amaas: {str(e)}")
            return "failed"
