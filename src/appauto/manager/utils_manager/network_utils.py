import socket
from time import sleep, time
import ping3
from appauto.manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


class NetworkUtils:
    @classmethod
    def check_pingable(cls, ip, timeout_s: int = 3):
        if response_time_ms := ping3.ping(ip, timeout_s):
            logger.info(f"{ip} can be pinged, response time: {response_time_ms}ms")
            return True
        logger.info(f"Unable to ping {ip}")
        return False

    @classmethod
    def check_sshable(cls, ip, port=22):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((ip, port))
            logger.info(f"{ip}:{port} is reachable")
            return True
        except (socket.timeout, ConnectionRefusedError):
            logger.info(f"{ip}:{port} is unreachable")
            return False
        finally:
            sock.close()

    @classmethod
    def wait_pingable(cls, ip, interval_s: int = 1, timeout_s: int = 600):
        start_time = time()
        while True:
            if cls.check_pingable(ip):
                break
            elif time() - start_time >= timeout_s:
                raise TimeoutError(f"Timeout while waiting for {ip} be pingable.")
            sleep(interval_s)

    @classmethod
    def wait_sshable(cls, ip, port=22, interval_s: int = 1, timeout_s: int = 600):
        start_time = time()
        while True:
            if cls.check_sshable(ip, port):
                break
            elif time() - start_time >= timeout_s:
                raise TimeoutError(f"Timeout while waiting for {ip} be sshable.")
            sleep(interval_s)

    @classmethod
    def get_local_ip(cls):
        """
        查询本机 ip 地址
        :return: ip
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
