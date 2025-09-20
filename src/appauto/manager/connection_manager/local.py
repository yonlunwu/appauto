import os
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

    @classmethod
    def delete_file(cls, file_path):
        """
        删除指定路径的文件

        参数:
            file_path (str): 要删除的文件的路径

        返回:
            bool: 删除成功返回True，失败返回False
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"错误: 文件 '{file_path}' 不存在")
                return False

            if not os.path.isfile(file_path):
                logger.error(f"错误: '{file_path}' 不是一个文件")
                return False

            os.remove(file_path)
            logger.info(f"文件 '{file_path}' 已成功删除")
            return True

        except PermissionError:
            logger.error(f"错误: 没有权限删除文件 '{file_path}'")
        except OSError as e:
            logger.error(f"错误: 删除文件时发生系统错误 - {e}")
        except Exception as e:
            logger.error(f"错误: 删除文件时发生意外错误 - {e}")

        return False
