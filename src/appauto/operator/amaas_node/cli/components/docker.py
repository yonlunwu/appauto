from typing import Literal, Optional, Dict, List
from appauto.manager.client_manager import BaseLinux
from appauto.manager.utils_manager.format_output import remove_line_break
from appauto.manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


# TODO wuhao 帮忙补充完整
class AMaaSDocker(BaseLinux):
    def __init__(self, mgt_ip, ssh_user="qujing", ssh_password="madsys123", ssh_port=22):
        super().__init__(mgt_ip, ssh_user, ssh_password, ssh_port)

    def stop(self, ctn_name):
        self.run(f"docker stop {ctn_name}")

    def get_ctn_id_by_name(self, ctn_name="zhiwen-ft") -> Optional[str]:
        cmd = f'docker ps -a --filter "name=^/{ctn_name}$" --format {"{{.ID}}"}'
        rc, res, _ = self.run(cmd)
        if rc == 0:
            return remove_line_break(res)

    # 一次性查询获取所有 map
    def get_ctn_names_ids_map(self, ctn_names: List = None) -> Dict[str, Optional[str]]:
        assert ctn_names and isinstance(ctn_names, list)

        ctn_names_set = set(ctn_names)

        cmd = 'docker ps -a --format "{{.ID}}:{{.Names}}"'
        rc, res, _ = self.run(cmd)

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
        rc, res, _ = self.run(cmd)
        if rc == 0:
            if "true" in res:
                return "yes"
            elif "false" in res:
                return "no"

        return "unknown"

    def stop_ctn(self, ctn_id):
        is_running = self.is_running(ctn_id)

        if is_running == "yes":
            self.run_with_check(f"docker stop {ctn_id}")

        elif is_running == "no":
            return

        elif is_running == "unknown":
            logger.info(f"ctn {ctn_id} status is unknown, but try to stop it.")
            self.run(f"docker stop {ctn_id}")

        assert self.is_running(ctn_id) == "no"

        logger.info(f"{ctn_id} has been stopped.")

    def rm_ctn(self, ctn_id):
        cmd = f"docker rm {ctn_id}"
        self.run_with_check(cmd)

        logger.info(f"{ctn_id} has been removed.")

    def restart_ctn(self, ctn_id):
        cmd = f"docker restart {ctn_id}"
        self.run_with_check(cmd)

    def prune(self, resource: Literal["network", "image", "container", "system"]):
        cmd = f"sudo docker {resource} prune -f"
        self.run(cmd, sudo=False)

    def decompress(self, tar_name: str):
        cmd = f"cd {self.deploy_path} && sudo tar -zxvf {tar_name}"
        self.run(cmd, sudo=False)

    def have_tar(self, tar_name: str) -> Literal["yes", "no", "unknown"]:
        try:
            cmd = f"test -f {self.deploy_path}{tar_name}"
            rc, _, _ = self.run(cmd)

            if rc == 0:
                return "yes"

            return "no"

        except Exception as e:
            return "unknown"
