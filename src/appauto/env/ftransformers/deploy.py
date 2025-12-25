"""
引擎 dev 通常会给一个 ft-test 包, 我们需要 load 并运行起来.
"""

import os
from typing import Literal
from string import Template
from appauto.manager.config_manager.config_logging import LoggingConfig

from ..base_deploy import BaseDeploy

logger = LoggingConfig.get_logger()


class DeployFT(BaseDeploy):
    def __init__(
        self,
        mgt_ip,
        ssh_user="qujing",
        ssh_password="madsys123",
        ssh_port=22,
        deploy_path="/mnt/data/deploy/",
        ctn_name: str = None,
    ):
        super().__init__(mgt_ip, ssh_user, ssh_password, ssh_port, deploy_path)
        self.ctn_names = self.set_ctn_name(ctn_name)

    def set_ctn_name(self, ctn_name=None):

        if ctn_name:
            return ctn_name

        if self.gpu_type == "huawei":
            return "zhiwen-ft-ascend"

        return "zhiwen-ft"

    def gen_docker_compose(
        self,
        image="zhiwen-ftransformers",
        tag="v3.3.0-test2",
        output="ft-docker-compose",
    ) -> str:
        """
        使用 Template 生成 docker-compose.yaml 配置文件

        参数:
            - ctn_name: 容器名称
            - mac_address: 网卡 MAC
            - image: 镜像名称
            - tag: 镜像 tag
            - output: 输出文件前缀, 最终是: $output_$tag.yaml
        """
        template_content = """services:
  $ctn_name:
    image: $image:$tag
    container_name: $ctn_name
    shm_size: "64GB"
    privileged: true
    network_mode: host
    volumes:
      - /mnt/data/models:/mnt/data/models
    restart: always
    entrypoint: ["sleep", "infinity"]
    environment:
      - "TZ=Asia/Shanghai"
      - "MAC_ADDRESS=$mac_address"
      - "NVIDIA_VISIBLE_DEVICES=all"
    deploy:
      resources:
        reservations:
          devices:
            - driver: "nvidia"
              count: "all"
              capabilities: [ "gpu" ]
    """

        template = Template(template_content)

        config_content = template.substitute(
            ctn_name=self.ctn_names,
            mac_address=self.nic_mac_addr,
            image=image,
            tag=tag,
        )

        output = f"{output}_{tag}.yaml"
        with open(output, "w") as f:
            f.write(config_content)

        logger.info(f"配置文件已生成: {os.path.abspath(output)}")

        return output

    def deploy(
        self,
        tar_name,
        output="ft-docker-compose",
        stop_old=True,
    ) -> Literal["succeed", "failed"]:
        """
    部署 ft 镜像, 请先在 cls.deploy_path(默认 /mnt/data/deploy) 下上传新的 tar 包.

    参数:
        ### 直接部署:
        - tar_name: tar 包, 如: zhiwen-ftransformers-v3.3.0-test4.tar
        - output: 输出文件前缀, 最终是: $output_<image_ref>.yaml (由 tar 内镜像信息决定)

        ### 停掉旧 container
        - stop_old: bool
        """

        try:
            # 检查是否有 tar
            assert self.have_tar(tar_name) == "yes", f"The {tar_name} doesn't exist."

            # 先 load 新镜像，解析出 image:tag（image_ref）
            image, tag = self.docker_tool.load_image(f"{self.deploy_path}{tar_name}")
            assert image and tag, f"load image failed from tar: {tar_name}"

            if cur_ctn_id := self.docker_tool.get_ctn_id_by_name(self.ctn_names):
                # 停止旧容器
                if stop_old:
                    self.docker_tool.stop_ctn(cur_ctn_id)

                self.docker_tool.rm_ctn(cur_ctn_id)

            # 不删旧的image

            # 部署新容器：compose 直接写 image_ref
            docker_compose = self.gen_docker_compose(image=image, tag=tag, output=output)
            
            self.upload(f"{self.deploy_path}{docker_compose}", docker_compose)

            self.docker_tool.up_ctn_from_compose(self.deploy_path, docker_compose)

            ctn_id = self.docker_tool.get_ctn_id_by_name(self.ctn_names)
            assert self.docker_tool.is_running(ctn_id) == "yes"

            return "succeed"

        except Exception as e:
            logger.error(f"error occurred while deploying zhiwen-ft: {str(e)}")
            return "failed"
