import subprocess
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class Local:
    @classmethod
    def run(cls, cmd):
        """
        在本地运行命令，并获取返回码、标准输出和标准错误。

        :param command: 要运行的命令字符串
        :return: 返回码、标准输出、标准错误
        """
        try:
            # 使用 subprocess.run 运行命令
            logger.info(f"running {cmd} on Local.")
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            rc = result.returncode
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

        except Exception as e:
            rc = -1
            stdout = ""
            stderr = str(e)

        logger.info(f"STDOUT: {stdout}")
        if stderr:
            logger.error(f"STDERR: {stderr}")

        return rc, stdout, stderr
