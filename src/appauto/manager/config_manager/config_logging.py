import logging.config
import os
import time
from pathlib import Path
from ..file_manager.handle_ini import HandleIni


class LoggingConfig:
    LOGGING_INI = "logging.ini"

    @classmethod
    def init(cls):
        content = """
[loggers]
keys=root

[handlers]
keys=consoleHandler, rootHandler, RotatingFileHandler

[formatters]
keys=sampleFormatter

[logger_root]
level=INFO
handlers=consoleHandler, RotatingFileHandler
qualname=root
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=sampleFormatter
args=(sys.stdout,)

[handler_rootHandler]
class=FileHandler
level=INFO
formatter=sampleFormatter
args=(os.path.join(os.getcwd(), 'logs/root.log'),)

[handler_RotatingFileHandler]
class=handlers.RotatingFileHandler
level=INFO
formatter=sampleFormatter
args=(os.path.join(os.getcwd(), 'logs/root.log'), 'a', 10485760, 30)

[formatter_sampleFormatter]
format=%(asctime)s|%(process)d:%(threadName)s:%(thread)d|%(name)s|%(levelname)-4s|[%(filename)s:%(lineno)d]|%(message)s
"""

        with open(cls.LOGGING_INI, "w", encoding="utf-8") as file:
            file.write(content.lstrip())

    @classmethod
    def config_logging(
        cls, log_level: str = "INFO", file_size: int = 10485760, file_count: int = 200, timestamp: str = None
    ):
        log_ini = HandleIni(Path(cls.LOGGING_INI))
        timestamp = timestamp or time.strftime("%Y%m%d_%H%M%S", time.localtime())

        # 读取现有配置
        if not log_ini.config.has_section("formatters"):
            log_ini.config.add_section("formatters")

        updates = {}

        # 配置 log_level
        for sec in ["logger_root", "handler_consoleHandler", "handler_rootHandler", "handler_RotatingFileHandler"]:
            # 获取现有配置
            cur_cfg = dict(log_ini.config.items(sec))
            if cur_cfg["level"] != log_level:
                updates[sec] = cur_cfg
                updates[sec]["level"] = log_level

        # 配置 handler_RotatingFileHandler.args
        cur_cfg = dict(log_ini.config.items("handler_RotatingFileHandler"))
        if "handler_RotatingFileHandler" not in updates:
            updates["handler_RotatingFileHandler"] = cur_cfg
        updates["handler_RotatingFileHandler"]["args"] = str(
            (
                os.path.join(os.getcwd(), f"logs/root_{timestamp}.log"),
                "a",
                file_size,
                file_count,
            )
        )

        # 配置 handler_rootHandler.args
        cur_cfg = dict(log_ini.config.items("handler_rootHandler"))
        if "handler_rootHandler" not in updates:
            updates["handler_rootHandler"] = cur_cfg
        updates["handler_rootHandler"]["args"] = str((os.path.join(os.getcwd(), f"logs/root_{timestamp}.log"),))

        if updates:
            for o_k, o_v in updates.items():
                for i_k, i_v in o_v.items():
                    log_ini.config.set(o_k, i_k, i_v)
            log_ini.write()

    @classmethod
    def joint_path(cls, file: str = None):
        root = Path(__file__).resolve()
        parent_dir = root.parents[4]
        pyproject_path = parent_dir / (file or cls.LOGGING_INI)

        return pyproject_path

    @classmethod
    def check_logging_ini(cls):
        return bool(os.path.isfile(cls.LOGGING_INI))

    @classmethod
    def get_logger(cls, logger="root"):
        if not cls.check_logging_ini():
            cls.init()
        logging.config.fileConfig(
            fname=cls.joint_path(),
            defaults=os.makedirs("logs", exist_ok=True),
            disable_existing_loggers=False,
        )
        return logging.getLogger(logger)
