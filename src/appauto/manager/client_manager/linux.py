from appauto.manager.connection_manager.ssh import SSHClient
from appauto.manager.config_manager.config_logging import LoggingConfig
from tenacity import retry, stop_after_attempt, wait_fixed, wait_chain
from paramiko.ssh_exception import (
    NoValidConnectionsError,
    ChannelException,
    AuthenticationException,
    BadAuthenticationType,
    BadHostKeyException,
    SSHException,
    ProxyCommandFailure,
)
from typing import Tuple, Optional

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

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_chain(*[wait_fixed(3) for _ in range(5)] + [wait_fixed(5) for _ in range(3)] + [wait_fixed(10)]),
        reraise=True,
    )
    def run(
        self, cmd, sudo=True, shell=False, print_screen=False, timeout=None
    ) -> Tuple[int, Optional[str], Optional[str]]:
        try:
            if sudo and shell:
                cmd = f'echo "{cmd}" | sudo /bin/bash'
            elif sudo:
                cmd = f"sudo {cmd}"
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
