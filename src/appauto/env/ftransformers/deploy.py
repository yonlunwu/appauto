"""
引擎 dev 通常会给一个 ft-test 包, 我们需要 load 并运行起来.
"""

import os
from typing import Tuple
from string import Template
from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig
from appauto.manager.utils_manager.format_output import remove_line_break

from ..base_deploy import BaseDeploy

logger = LoggingConfig.get_logger()


class DeployFT(BaseDeploy):
    deploy_path = "/mnt/data/deploy/"

    def __init__(self, amaas, deploy_path="/mnt/data/deploy/", ctn_name="zhiwen-ft"):
        super().__init__(amaas, deploy_path)
        self.ctn_names = ctn_name

    def gen_docker_compose(
        self,
        image="zhiwen-ftransformers",
        tag="v3.3.0-test2",
        host_port=30000,
        ctn_port=30000,
        output="ft-docker-compose",
    ) -> str:
        """
        使用 Template 生成 docker-compose.yaml 配置文件

        参数:
            - ctn_name: 容器名称
            - mac_address: 网卡 MAC
            - image: 镜像名称
            - tag: 镜像 tag
            - host_port: 宿主机 port
            - ctn_port: 容器 port
            - output: 输出文件前缀, 最终是: $output_$tag.yaml
        """
        template_content = """services:
  $ctn_name:
    image: $image:$tag
    container_name: $ctn_name
    shm_size: "32GB"
    privileged: true
    volumes:
      - /mnt/data/models:/mnt/data/models
    restart: always
    entrypoint: ["sleep", "infinity"]
    environment:
      - "TZ=Asia/Shanghai"
      - "MAC_ADDRESS=$mac_address"
      - "NVIDIA_VISIBLE_DEVICES=all"
    ports:
      - "$host_port:$ctn_port"
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
            mac_address=self.amaas.cli.nic_mac_addr,
            image=image,
            tag=tag,
            host_port=host_port,
            ctn_port=ctn_port,
        )

        output = f"{output}_{tag}.yaml"
        with open(output, "w") as f:
            f.write(config_content)

        logger.info(f"配置文件已生成: {os.path.abspath(output)}")

        return output

    def load_tar(self, tar_name: str):
        """
        tar_name: 包名, 如: zhiwen-ftransformers-v3.3.0-test2.tar
        """
        cmd = f"docker load -i {self.deploy_path}{tar_name}"
        self.amaas.cli.run_with_check(cmd)

    def up_ctn_from_compose(self, compose_file: str):
        cmd = f"cd {self.deploy_path} && sudo docker compose -f {compose_file} up -d"
        self.amaas.cli.run_with_check(cmd, sudo=False)

    def deploy(
        self,
        tar_name,
        image="zhiwen-ftransformers",
        tag="v3.3.0-test2",
        host_port=30000,
        ctn_port=30000,
        output="ft-docker-compose",
        stop_old=False,
    ) -> str:
        """
        部署 ft 镜像, 请先在 cls.deploy_path(默认 /mnt/data/deploy) 下传新的 image, 如果需要停止旧的, 也请传入旧容器和旧 tag.

        参数:
            ### 直接部署:
            - tar_name: tar 包, 如: zhiwen-ftransformers-v3.3.0-test4.tar
            - image: 镜像名称
            - tag: 镜像 tag
            - host_port: 宿主机 port
            - ctn_port: 容器 port
            - output: 输出文件前缀, 最终是: $output_$tag.yaml

            ### 停掉旧 container
            - stop_old: bool

        步骤:
            1. 停止和删除旧容器
            2. load 镜像并部署新容器
        """

        # 检查是否有 image
        assert self.have_tar(tar_name) == "yes"

        cur_ctn_id = self.get_ctn_id_by_name(self.ctn_names)

        # 停止旧容器
        if stop_old:
            self.stop_ctn(cur_ctn_id)

        self.rm_ctn(cur_ctn_id)

        # 部署新容器
        docker_compose = self.gen_docker_compose(image, tag, host_port, ctn_port, output)

        self.amaas.cli.upload(f"{self.deploy_path}{docker_compose}", docker_compose)

        self.load_tar(tar_name)

        self.up_ctn_from_compose(docker_compose)

        ctn_id = self.get_ctn_id_by_name(self.ctn_names)
        assert self.is_running(ctn_id) == "yes"

        logger.info(f"{self.ctn_names}:{tag} has been deployed.")
