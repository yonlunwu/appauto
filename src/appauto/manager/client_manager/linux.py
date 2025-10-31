import os
from time import sleep, time
from queue import Queue
from threading import Thread
from functools import cached_property
from paramiko.ssh_exception import (
    NoValidConnectionsError,
    ChannelException,
    AuthenticationException,
    BadAuthenticationType,
    BadHostKeyException,
    SSHException,
    ProxyCommandFailure,
)
from typing import Tuple, Optional, Literal, List, TYPE_CHECKING
from tenacity import retry, stop_after_attempt, wait_fixed, wait_chain

from ..connection_manager.ssh import SSHClient
from ..config_manager import LoggingConfig
from ..utils_manager.format_output import str_to_list_by_split, remove_line_break

if TYPE_CHECKING:
    from .components.docker import BaseDockerTool

logger = LoggingConfig.get_logger()


class BaseLinux(object):
    def __init__(self, mgt_ip, ssh_user="qujing", ssh_password="madsys123", ssh_port=22):
        self.mgt_ip = mgt_ip
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_port = ssh_port
        self.ssh = SSHClient.estab_connect(mgt_ip, ssh_user, ssh_password, ssh_port)

    def __str__(self):
        return self.mgt_ip

    @cached_property
    def docker_tool(self) -> "BaseDockerTool":
        return BaseDockerTool(self)

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_chain(*[wait_fixed(3) for _ in range(5)] + [wait_fixed(5) for _ in range(3)] + [wait_fixed(10)]),
        reraise=True,
    )
    def run(
        self, cmd, sudo=True, bash=False, shell=False, print_screen=False, timeout=None
    ) -> Tuple[int, Optional[str], Optional[str]]:
        try:
            if sudo and shell:
                cmd = f'echo "{cmd}" | sudo /bin/bash'
            elif sudo:
                cmd = f"sudo {cmd}"
            elif bash:
                cmd = f"bash -i -c '{cmd}'"
            elif shell:
                cmd = f'echo "{cmd}" | /bin/bash'

            logger.info(f"running {cmd} on {self}")
            _, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)

            if print_screen:
                while not stdout.channel.exit_status_ready():
                    if stdout.channel.recv_ready():
                        line = stdout.channel.recv(4096).decode("utf-8")
                        logger.info(f"STDOUT: {line.strip()}")
                    if stderr.channel.recv_ready():
                        line = stderr.channel.recv(4096).decode("utf-8")
                        logger.info(f"STDERR: {line.strip()}")

            stdouts = stdout.read().decode("utf-8")
            logger.info(f"STDOUT: {stdouts}")
            stderrs = stderr.read().decode("utf-8")
            if stderrs != "":
                logger.info(f"STDERR: {stderrs}")

            rc = stdout.channel.recv_exit_status()
            return rc, stdouts, stderrs

        except (
            AuthenticationException,
            BadAuthenticationType,
            BadHostKeyException,
        ) as e:
            logger.error(f"Error occurred that will not be retried: {e}")
        except (
            NoValidConnectionsError,
            ChannelException,
            SSHException,
            ProxyCommandFailure,
        ) as e:
            logger.error(f"Error occurred that will be retried: {e}")
            self.ssh = SSHClient.estab_connect(self.mgt_ip, self.ssh_user, self.ssh_passwd)
            raise e

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_chain(*[wait_fixed(10) for _ in range(3)] + [wait_fixed(20) for _ in range(2)] + [wait_fixed(30)]),
        reraise=True,
    )
    def run_with_check(
        self, cmd, sudo=True, bash=False, shell=False, print_screen=False, timeout=None
    ) -> Tuple[int, Optional[str], Optional[str]]:
        try:
            if sudo and shell:
                cmd = f'echo "{cmd}" | sudo /bin/bash'
            elif sudo:
                cmd = f"sudo {cmd}"
            elif bash:
                cmd = f"bash -i -c '{cmd}'"
            elif shell:
                cmd = f'echo "{cmd}" | /bin/bash'

            logger.info(f"running {cmd} on {self}")
            _, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)

            if print_screen:
                while not stdout.channel.exit_status_ready():
                    if stdout.channel.recv_ready():
                        line = stdout.channel.recv(4096).decode("utf-8")
                        logger.info(f"STDOUT: {line.strip()}")
                    if stderr.channel.recv_ready():
                        line = stderr.channel.recv(4096).decode("utf-8")
                        logger.info(f"STDERR: {line.strip()}")

            stdouts = stdout.read().decode("utf-8")
            logger.info(f"STDOUT: {stdouts}")
            stderrs = stderr.read().decode("utf-8")
            if stderrs != "":
                logger.info(f"STDERR: {stderrs}")

            rc = stdout.channel.recv_exit_status()
            assert rc == 0
            return rc, stdouts, stderrs

        except (
            AuthenticationException,
            BadAuthenticationType,
            BadHostKeyException,
        ) as e:
            logger.error(f"Error occurred that will not be retried: {e}")
        except (
            NoValidConnectionsError,
            ChannelException,
            SSHException,
            ProxyCommandFailure,
        ) as e:
            logger.error(f"Error occurred that will be retried: {e}")
            self.ssh = SSHClient.estab_connect(self.mgt_ip, self.ssh_user, self.ssh_passwd)
            raise e

    def run_in_docker(
        self, ctn_name: str, cmd: str, print_screen=False, timeout=None
    ) -> Tuple[int, Optional[str], Optional[str]]:
        """
        需要提前将当前的 ssh_user 加入到 docker 组，否则会报权限错误
        """
        try:
            cmd = f"docker exec {ctn_name} bash -c '{cmd}'"

            logger.info(f"running {cmd} on {self}")
            _, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)

            if print_screen:
                while not stdout.channel.exit_status_ready():
                    if stdout.channel.recv_ready():
                        line = stdout.channel.recv(4096).decode("utf-8")
                        logger.info(f"STDOUT: {line.strip()}")
                    if stderr.channel.recv_ready():
                        line = stderr.channel.recv(4096).decode("utf-8")
                        logger.info(f"STDERR: {line.strip()}")

            stdouts = stdout.read().decode("utf-8")
            logger.info(f"STDOUT: {stdouts}")
            stderrs = stderr.read().decode("utf-8")
            if stderrs != "":
                logger.info(f"STDERR: {stderrs}")

            rc = stdout.channel.recv_exit_status()
            return rc, stdouts, stderrs

        except (
            AuthenticationException,
            BadAuthenticationType,
            BadHostKeyException,
        ) as e:
            logger.error(f"Error occurred that will not be retried: {e}")
        except (
            NoValidConnectionsError,
            ChannelException,
            SSHException,
            ProxyCommandFailure,
        ) as e:
            logger.error(f"Error occurred that will be retried: {e}")
            self.ssh = SSHClient.estab_connect(self.mgt_ip, self.ssh_user, self.ssh_passwd)
            raise e

    def install_conda(self, type: Literal["miniconda", "anaconda"]):
        """安装 conda"""
        ...

    def run_in_thread(
        self, cmd, sudo=True, bash=False, shell=False, print_screen=False, timeout=None, start=True
    ) -> Tuple[Thread, Queue]:
        """
        异步执行 SSH 命令，返回执行线程和输出队列
        队列中内容为: ("STDOUT", str), ("STDERR", str), ("RC", int), 或 ("EXCEPTION", Exception)，结尾为 ("END", None)
        """

        def _worker(q: Queue):
            try:
                rc, stdouts, stderrs = self.run(cmd, sudo, bash, shell, print_screen, timeout)
                q.put(("STDOUT", stdouts))
                q.put(("STDERR", stderrs))
                q.put(("RC", rc))

            except Exception as e:
                logger.error(f"error occurred: {e}")
                q.put(("EXCEPTION", e))

            finally:
                q.put(("END", None))

        q = Queue()
        th = Thread(target=_worker, args=(q,), daemon=True)

        if start:
            th.start()

        return th, q

    def _grant_dir_permission(self, dir: str):
        """
        为 self.ssh_user 授予远程目录的读写权限

        :param remote_dir: 远程目录路径（如 /mnt/data/deploy）
        """
        try:
            # If the directory belongs to a group, add the user to the group and grant write permission to the group
            rc, group, stderr = self.run_with_check(f"stat -c '%G' {dir}")
            group = remove_line_break(group)

            # Add the user to the directory's group if not already a member
            rc, _, stderr = self.run(f"groups {self.ssh_user} | grep -w {group}")
            assert not stderr
            in_group = rc == 0

            if not in_group:  # User not in the group
                self.run(f"usermod -aG {group} {self.ssh_user}")

            # Grant write permission to the group
            self.run_with_check(f"chmod g+w {dir}")

            logger.info(f"Granted write permission for {dir} to user {self.ssh_user}")

        except Exception as e:
            raise Exception(f"Failed to set permissions: {str(e)}")

    def download(self, remote_path: str, local_path: str):
        sftp = self.ssh.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()

    def upload(self, remote_path: str, local_path: str, auto_fix_permission: bool = True):
        """
        上传文件到目标路径，支持自动修复目录权限

        :param remote_path: 远程目标文件路径（如 /mnt/data/deploy/file.txt)
        :param local_path: 本地文件路径
        :param auto_fix_permission: 是否自动修复目录权限（默认开启）
        """
        try:
            # Check local file existence
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file does not exist: {local_path}")

            remote_dir = os.path.dirname(remote_path)

            # Automatically fix permissions if enabled
            if auto_fix_permission:
                self._grant_dir_permission(remote_dir)

            # Directly upload to final directory (permissions should be sufficient now)
            sftp = self.ssh.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            logger.info(f"File uploaded directly to target path: {remote_path}")

        except SSHException as e:
            raise Exception(f"SSH command execution failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")

    def cpu_core(self):
        cmd = "lscpu | grep \"CPU(s)\" | head -n 1 | awk '{print $NF}'"
        _, res, _ = self.run(cmd)
        return res

    def conda_env_list(self, conda_path=None, sudo=False):
        # cmd = "bash -i -c 'echo $PATH && which conda && conda env list'"
        cmd = "bash -i -c 'conda env list'"
        return self.run(cmd, sudo=False)
        # _, res, _ = self.run(f"{conda_path or 'conda'} env list | tail -n +3 | awk '{{print $1}}' | head -n -1", sudo=sudo)
        # return str_to_list_by_split(res, singleLine=False)

    def get_process_id(self, process_name):
        rc, res, _ = self.run(f"pidof {process_name}", verbose=True)
        if rc == 0:
            return res

    def grep_pid(self, keyword) -> List:
        """
        ps aux | grep sglang.launch_server | grep -v grep | awk '{print $2}'
        """
        _, res, _ = self.run(f"ps aux | grep {keyword} | grep -v grep | awk '{{print $2}}'")
        return str_to_list_by_split(res, singleLine=False)

    def stop_process_by_name(self, process_name: str, interval_s: int = 15, timeout_s: int = 180, force=False):
        """停止进程. force 表示 -9, 否则 ctrl+c"""
        start_time = time()
        sig = "-9" if force else "-2"
        while True:
            if pid := self.get_process_id(process_name):
                self.run(f"kill {sig} {pid}")
                sleep(3)

            if not self.get_process_id(process_name):
                logger.info(f"kill {sig} {process_name} succeed.")
                return

            if time() - start_time >= timeout_s:
                raise TimeoutError(f"Timeout while waiting for kill {sig} {process_name} done.")

            sleep(interval_s)

    def stop_process_by_keyword(self, keyword, interval_s: int = 15, timeout_s: int = 180, force=False):
        """停止进程. force 表示 -9, 否则 ctrl+c"""
        start_time = time()
        sig = "-9" if force else "-2"
        while True:
            if pids := self.grep_pid(keyword):
                for pid in pids:
                    self.run(f"kill {sig} {pid}")
                sleep(3)

            if not self.grep_pid(keyword):
                logger.info(f"kill {sig} {keyword} succeed.")
                return

            if time() - start_time >= timeout_s:
                raise TimeoutError(f"Timeout while waiting for kill {sig} {keyword} done.")

            sleep(interval_s)
