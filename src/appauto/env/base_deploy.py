from typing import Literal, List, Union, Optional, Dict
from appauto.operator.amaas_node import AMaaSNode
from appauto.manager.config_manager.config_logging import LoggingConfig
from appauto.manager.utils_manager.format_output import remove_line_break

logger = LoggingConfig.get_logger()


class BaseDeploy:

    def __init__(self, amaas: AMaaSNode, deploy_path="/mnt/data/deploy/"):
        self.amaas = amaas
        self.deploy_path = deploy_path
        self.ctn_names: Union[List, str] = None

    def get_ctn_id_by_name(self, ctn_name="zhiwen-ft") -> Optional[str]:
        cmd = f'docker ps -a --filter "name={ctn_name}" --format {"{{.ID}}"}'
        rc, res, _ = self.amaas.cli.run(cmd)
        if rc == 0:
            return remove_line_break(res)

    # 查询效率低
    def get_ctn_names_ids_map(self, ctn_names: List = None) -> Dict[str, Optional[str]]:
        """
        ctn_names 为空时则默认用 self.ctn_names
        """
        ctn_names = ctn_names or self.ctn_names
        ctn_names = ctn_names if isinstance(ctn_names, list) else [ctn_names]

        return {name: self.get_ctn_id_by_name(name) for name in ctn_names}

    # 一次性查询获取所有 map
    def get_ctn_names_ids_map(self, ctn_names: List = None) -> Dict[str, Optional[str]]:
        """
        ctn_names 为空时则默认用 self.ctn_names
        """
        ctn_names = ctn_names or self.ctn_names
        ctn_names = ctn_names if isinstance(ctn_names, list) else [ctn_names]

        ctn_names_set = set(ctn_names)

        cmd = 'docker ps -a --format "{{.ID}}:{{.Names}}"'
        rc, res, _ = self.amaas.cli.run(cmd)

        if rc != 0:
            return {name: None for name in ctn_names}

        ctn_id_map = {}
        for line in res.splitlines():
            line = line.strip()

            if not line:
                continue

            ctn_id, names = line.split(":")

            for name in names.split(","):  # 一个容器可能有多个名称
                for target in ctn_names_set:
                    if target == name.strip():
                        ctn_id_map[target] = ctn_id
                        ctn_names_set.remove(target)
                        break

            if not ctn_names_set:  # 所有目标都找到，提前退出
                break

        # 为未找到的容器填充 None
        for name in ctn_names:
            if name not in ctn_id_map:
                ctn_id_map[name] = None

        return ctn_id_map

    def is_running(self, ctn_id) -> Literal["yes", "no", "unknown"]:
        cmd = f"docker inspect -f {'{{.State.Running}}'} {ctn_id}"
        rc, res, _ = self.amaas.cli.run(cmd)
        if rc == 0:
            if "true" in res:
                return "yes"
            elif "false" in res:
                return "no"

        return "unknown"

    def stop_ctn(self, ctn_id):
        is_running = self.is_running(ctn_id)

        if is_running == "yes":
            self.amaas.cli.run_with_check(f"docker stop {ctn_id}")

        elif is_running == "no":
            return

        elif is_running == "unknown":
            logger.info(f"ctn {ctn_id} status is unknown, but try to stop it.")
            self.amaas.cli.run(f"docker stop {ctn_id}")

        assert self.is_running(ctn_id) == "no"

        logger.info(f"{ctn_id} has been stopped.")

    def rm_ctn(self, ctn_id):
        cmd = f"docker rm {ctn_id}"
        self.amaas.cli.run_with_check(cmd)

        logger.info(f"{ctn_id} has been removed.")

    def prune(self, resource: Literal["network", "image", "container", "system"]):
        cmd = f"sudo docker {resource} prune -f"
        self.amaas.cli.run(cmd, sudo=False)

    def decompress(self, tar_name: str):
        cmd = f"cd {self.deploy_path} && sudo tar -zxvf {tar_name}"
        self.amaas.cli.run(cmd, sudo=False)

    def have_tar(self, tar_name: str) -> Literal["yes", "no", "unknown"]:
        try:
            cmd = f"test -f {self.deploy_path}{tar_name}"
            rc, _, _ = self.amaas.cli.run(cmd)

            if rc == 0:
                return "yes"

            return "no"

        except Exception as e:
            return "unknown"
