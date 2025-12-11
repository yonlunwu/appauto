import re
from typing import Literal, Optional, Dict, List
from ..linux import BaseLinux
from ...utils_manager.format_output import remove_line_break
from ...config_manager.config_logging import LoggingConfig

from typing import List, Optional, Dict

logger = LoggingConfig.get_logger()


# 工具类，封装常用的 docker 命令行操作
class BaseDockerTool:
    def __init__(self, node: BaseLinux):
        self.node = node

    def get_ctn_id_by_name(self, ctn_name: str = None) -> Optional[str]:
        cmd = f'docker ps -a --filter "name=^/{ctn_name}$" --format {"{{.ID}}"}'
        rc, res, _ = self.node.run(cmd)
        if rc == 0:
            return remove_line_break(res)

    def get_ctn_ip(self, ctn_id: str = None, ctn_name=None, sudo=False) -> Optional[str]:
        assert ctn_id or ctn_name, "Either ctn_id or ctn_name must be provided."
        tgt = ctn_id or ctn_name
        cmd = f"docker inspect -f '{'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'}' {tgt}"
        rc, res, _ = self.node.run(cmd, sudo)
        if rc == 0:
            return remove_line_break(res)

    def load_image(self, full_tar_path: str):
        cmd = f"docker load -i {full_tar_path}"
        self.node.run_with_check(cmd)

    # 一次性查询获取所有 map
    def get_ctn_names_ids_map(self, ctn_names: List = None) -> Dict[str, Optional[str]]:
        assert ctn_names and isinstance(ctn_names, list)

        ctn_names_set = set(ctn_names)

        cmd = 'docker ps -a --format "{{.ID}}:{{.Names}}"'
        rc, res, _ = self.node.run(cmd)

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

    def is_running(self, ctn_id: str) -> Literal["yes", "no", "unknown"]:
        cmd = f"docker inspect -f {'{{.State.Running}}'} {ctn_id}"
        rc, res, _ = self.node.run(cmd)
        if rc == 0:
            if "true" in res:
                return "yes"
            elif "false" in res:
                return "no"

        return "unknown"

    def stop_ctn(self, ctn_id: str):
        is_running = self.is_running(ctn_id)

        if is_running == "yes":
            self.node.run_with_check(f"docker stop {ctn_id}")

        elif is_running == "no":
            return

        elif is_running == "unknown":
            logger.info(f"ctn {ctn_id} status is unknown, but try to stop it.")
            self.node.run(f"docker stop {ctn_id}")

        assert self.is_running(ctn_id) == "no"

        logger.info(f"{ctn_id} has been stopped.")

    def have_resource(self, type_: Literal["image", "container"], id_: str) -> Literal["yes", "no", "unknown"]:
        try:
            cmd = f"docker inspect --type={type_} {id_} > /dev/null 2>&1; echo $?"
            rc, _, _ = self.node.run(cmd)

            if rc == 0:
                return "yes"

            return "no"

        except Exception as e:
            logger.error(f"error occurred when detect if image exist: {str(e)}")
            return "unknown"

    def rm_ctn(self, ctn_id: str):
        if self.have_resource("container", ctn_id):
            cmd = f"docker rm {ctn_id}"
            self.node.run_with_check(cmd)

            logger.info(f"{ctn_id} has been removed.")

    def rm_image_by_id(self, image_id: str, force=False):
        if self.have_resource("image", image_id):
            cmd = f"docker rmi {image_id} {'-f' if force else ''}"
            self.node.run_with_check(cmd)

            logger.info(f"{image_id} has been removed.")

    def rm_image_by_tag(self, image_name: str, tag: str, force=False):
        cmd = f"docker rmi {image_name}:{tag} {'-f' if force else ''}"
        self.node.run(cmd)

    def restart_ctn(self, ctn_id: str):
        cmd = f"docker restart {ctn_id}"
        self.node.run_with_check(cmd)

    def prune(self, resource: Literal["network", "image", "container", "system"]):
        cmd = f"docker {resource} prune -f"
        self.node.run(cmd, sudo=False)

    def _get_compose_cmd(self) -> str:
        candidate_cmds = [("docker compose", "V2"), ("docker-compose", "V1")]

        for cmd, version in candidate_cmds:
            try:
                check_cmd = f"{cmd} --help"
                rc, res, _ = self.node.run(check_cmd)

                if rc == 0:
                    if re.search(r"(-f|--file)", res):
                        logger.info(f"Find Docker Compose cmd that support the -f option:: {cmd} ({version})")
                        return cmd

                    logger.warning(f"Docker Compose cmd {cmd} ({version}) exists, but the -f option is not supported.")

            except Exception as e:
                logger.error(f"error occurred while get compose cmd, error: {e}")
                continue

        raise RuntimeError(
            "No Docker Compose or docker-compose cmds supporting the -f/--file option were found. "
            "Please check your Docker installation and version."
        )

    def up_ctn_from_compose(self, path: str, compose_file: str):
        compose_cmd = self._get_compose_cmd()

        cmd = f"cd {path} && sudo {compose_cmd} -f {compose_file} up -d"
        self.node.run_with_check(cmd, sudo=False)
