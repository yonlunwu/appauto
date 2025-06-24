from pathlib import Path
from typing import Optional
from ..file_manager.handle_ini import HandleIni
from .config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


class PytestConfig:
    PYTEST_INI = "pytest.ini"

    def __init__(
        self,
        timestamp: str,
        test_dir: Path,
        test_classes: str = None,
        test_cases: str = None,
        allure_results_dir: Optional[Path] = None,
        log_level: str = "INFO",
        no_report: bool = False,
        collect_only: bool = False,
        case_level: str = None,
    ):
        self.test_dir = test_dir
        self.test_classes = test_classes
        self.test_cases = test_cases
        self.allure_results_dir = allure_results_dir or (test_dir / "allure-results")
        self.log_level = log_level
        self.collect_only = collect_only
        self.no_report = True if self.collect_only else no_report
        self.timestamp = timestamp
        self.case_level = case_level

    @classmethod
    def _init(cls):
        """生成初始的 pytest.ini 文件"""
        content = """
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 日志配置
log_level = INFO
log_format =%(asctime)s|%(process)d:%(threadName)s:%(thread)d|%(levelname)-4s|[%(filename)s:%(lineno)d]|%(message)s
log_date_format=%Y-%m-%d %H:%M:%S

addopts = --capture=sys -sv -p no:warnings --color=no

# 测试标记
markers =
    ci: marks tests as ci
    smoke: marks tests as smoke
    night: marks tests as night

"""
        with open(cls.PYTEST_INI, "w", encoding="utf-8") as file:
            file.write(content.lstrip())

    def _reconfig(self):
        """根据用户配置重新设置 pytest.ini"""
        pytest_ini = HandleIni(Path(self.PYTEST_INI))

        # 读取现有配置
        if not pytest_ini.config.has_section("pytest"):
            pytest_ini.config.add_section("pytest")

        cur_cfg = dict(pytest_ini.config.items("pytest"))

        updates = {}

        if "testpaths" not in cur_cfg or cur_cfg["testpaths"] != str(self.test_dir):
            updates["testpaths"] = str(self.test_dir)

        if self.test_classes and cur_cfg["python_classes"] != self.test_classes:
            updates["python_classes"] = str(self.test_classes)

        if self.test_cases and cur_cfg["python_functions"] != self.test_cases:
            updates["python_functions"] = str(self.test_cases)

        if cur_cfg["log_level"] != self.log_level:
            updates["log_level"] = self.log_level

        if self.collect_only:
            updates["addopts"] = cur_cfg["addopts"] + " --collect-only"

        if not self.no_report:
            updates["addopts"] = cur_cfg["addopts"] + f" --alluredir=allure-results/{self.timestamp} --clean-alluredir"

        if self.case_level:
            if "addopts" in updates:
                updates["addopts"] += f" -m {self.case_level}"
            else:
                updates["addopts"] = cur_cfg["addopts"] + f" -m {self.case_level}"

        if updates:
            for key, value in updates.items():
                pytest_ini.config.set("pytest", key, value)
            pytest_ini.write()
            logger.debug(f"Updated pytest.ini with: {updates}")

    def config_pytest_ini(self) -> Path:
        """init & reconfig pytest.ini"""
        # pytest.ini 应该放在测试目录的根目录下
        pytest_ini_path = self.test_dir.parent / self.PYTEST_INI

        # 生成初始配置文件
        self._init()

        # 根据用户配置重新设置
        self._reconfig()

        logger.info(f"Created pytest.ini at {pytest_ini_path}")
        return pytest_ini_path
