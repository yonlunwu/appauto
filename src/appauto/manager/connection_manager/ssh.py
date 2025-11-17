import logging

from tenacity import retry, stop_after_attempt, wait_fixed, wait_chain
import paramiko
from paramiko.ssh_exception import (
    NoValidConnectionsError,
    ChannelException,
    AuthenticationException,
    BadAuthenticationType,
    BadHostKeyException,
    SSHException,
    ProxyCommandFailure,
)


class SSHClient(object):
    @classmethod
    @retry(
        stop=stop_after_attempt(10),
        wait=wait_chain(*[wait_fixed(3) for _ in range(5)] + [wait_fixed(5) for _ in range(3)] + [wait_fixed(10)]),
        reraise=True,
    )
    def estab_connect(cls, ip, username, password, port=22):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, port=port)
            ssh.get_transport().set_keepalive(10)
            return ssh
        except AuthenticationException or BadHostKeyException or BadAuthenticationType:
            logging.error(f"Auth Failed, please check username: {username} and passwd: {password}")
        except paramiko.socket.error or paramiko.socket.timeout as sock_err:
            logging.error("Network Connection Failed:", str(sock_err))
            raise sock_err
        except (
            NoValidConnectionsError,
            ChannelException,
            SSHException,
            ProxyCommandFailure,
        ) as e:
            logging.error(f"Error occured while estab_connection: {e}")
            raise e
        return

    @classmethod
    @retry(
        stop=stop_after_attempt(20),
        wait=wait_chain(
            *[wait_fixed(3) for _ in range(10)],
            *[wait_fixed(10) for _ in range(6)],
            wait_fixed(30),
        ),
        reraise=True,
    )
    def ssh(cls, mgt_ip, cmds, ssh_user="root", ssh_password="HC!r0cks"):
        sshClient = paramiko.SSHClient()
        sshClient.load_system_host_keys()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.connect(mgt_ip, port=22, username=ssh_user, password=ssh_password)
        try:
            logging.info(f"running cmd: {cmds} on host {mgt_ip}")
            _, stdout, stderr = sshClient.exec_command(cmds)
            res_out, res_err = stdout.read().decode("utf-8"), stderr.read().decode("utf-8")
            logging.info(f"the return stdout: \n{res_out}")
            if res_err:
                logging.error(f"the return stderr: \n{res_err}")
            return res_out, res_err
        except Exception as e:
            logging.error(f"error:{e}, ssh {mgt_ip} failed with {ssh_user}, {ssh_password} ".center(100, "-"))
            raise e
        finally:
            sshClient.close()
