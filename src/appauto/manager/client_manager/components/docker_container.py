import threading
from time import time, sleep
from queue import Queue
from functools import cached_property
from typing import Literal, Tuple, List

from ..linux import BaseLinux
from .docker import BaseDockerTool
from appauto.manager.config_manager.config_logging import LoggingConfig
from appauto.manager.utils_manager.format_output import str_to_list_by_split

logger = LoggingConfig.get_logger()


# Container 对象类
class BaseDockerContainer:
    def __init__(self, node: BaseLinux, name: str):
        self.node = node
        self.name = name
        self.docker_tool = BaseDockerTool(self.node)

    @cached_property
    def ctn_id(self) -> str:
        return self.docker_tool.get_ctn_id_by_name(self.name)

    @cached_property
    def ip(self):
        return self.docker_tool.get_ctn_ip(self.name)

    def check_server_reachable(self, port: int) -> bool:
        cmd = f"nc -zv {self.ip} {port}"
        rc, _, _ = self.node.run(cmd)
        if rc == 0:
            return True
        return False

    def wait_server_reachable(self, port: int, interval_s: int = 20, timeout_s: int = 300) -> bool:
        start_time = time()

        while True:
            if self.check_server_reachable(port):
                return True
            elif time() - start_time >= timeout_s:
                raise TimeoutError(f"Timeout while waiting for {self.ip}:{port} to be reachable.")
            sleep(interval_s)

    def run(self, cmd: str, sudo=False, print_screen=False, timeout=None):
        full_cmd = f"docker exec {self.name} bash -c '{cmd}'"
        return self.node.run(full_cmd, sudo, False, False, print_screen, timeout)

    def run_in_thread(
        self, cmd: str, sudo=False, start=True, print_screen=False, timeout=None
    ) -> Tuple[threading.Thread, Queue]:

        def _worker(q: Queue):
            try:
                full_cmd = f"docker exec {self.name} bash -c '{cmd}'"

                rc, stdouts, stderrs = self.node.run(full_cmd, sudo, False, False, print_screen, timeout)
                q.put(("STDOUT", stdouts))
                q.put(("STDERR", stderrs))
                q.put(("RC", rc))

            except Exception as e:
                logger.error(f"error occurred: {e}")
                q.put(("EXCEPTION", e))

            finally:
                q.put(("END", None))

        q = Queue()
        th = threading.Thread(
            target=_worker,
            args=(q,),
        )

        if start:
            th.start()

        return th, q

    @property
    def is_running(self) -> Literal["yes", "no", "unknown"]:
        return self.docker_tool.is_running(self.ctn_id())

    def stop(self):
        self.docker_tool.stop_ctn(self.ctn_id)

        assert self.is_running == "no"

    def rm(self):
        self.docker_tool.rm_ctn(self.ctn_id)

    def restart(self):
        self.docker_tool.restart_ctn(self.ctn_id)

        assert self.is_running == "yes"

    def launch_model(self): ...

    def get_running_model_pids(self, engine: str, model_name: str) -> List:
        return self.node.grep_pid(engine, model_name)

    def wait_model_to_running(
        self,
        port,
        interval_s=20,
        timeout_s=900,
    ):
        self.wait_server_reachable(port, interval_s, timeout_s)
        assert self.check_server_reachable(port)
