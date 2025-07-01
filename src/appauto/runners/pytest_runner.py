import subprocess
from ..manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


class PytestRunner:
    def __init__(
        self,
        timestamp,
        log_level: str = "INFO",
        notify_group: str = None,
        notify_user: str = None,
        repeat: int = 1,
        interval: int = 0,
        no_report: bool = False,
        testpaths: str = None,
        task_id: str = None,
        keyword: str = None,
        report_server: str = None,
        report_url: str = None,
        topic: str = None,
    ):
        self.log_level = log_level
        self.notify_group = notify_group
        self.notify_user = notify_user
        self.repeat = repeat
        self.interval = interval
        self.no_report = no_report
        self.testpaths = testpaths
        self.timestamp = timestamp
        self.task_id = task_id
        # # TODO 后期会考虑 task_id
        self.json_report_file = (
            f"{self.timestamp}_{self.task_id}.json" if self.task_id else f"reports/json-report/{self.timestamp}.json"
        )
        self.keyword = keyword
        self.report_server = report_server
        self.report_url = report_url
        self.topic = topic

    def run(self) -> int:
        """运行 pytest 命令"""
        cmd = [
            "pytest",
            "-sv",
            f"--timestamp={self.timestamp}",
            f"--log-cli-level={self.log_level}",
            f"--notify_group={self.notify_group}",
            f"--notify_user={self.notify_user}",
            f"--count={self.repeat}",
            f"--interval={self.interval}",
            f"--no_report={self.no_report}",
            f"--testpaths={self.testpaths}",
            "--json-report",
            f"--json-report-file={self.json_report_file}",
        ]

        if self.keyword:
            cmd.append(f"-k {self.keyword}")
        if self.report_server:
            cmd.append(f"--report_server={self.report_server}")
        if self.report_url:
            cmd.append(f"--report_url={self.report_url}")
        if self.topic:
            cmd.append(f"--topic={self.topic}")
        logger.info(f"Running pytest cmd: {' '.join(cmd)}")

        # 执行命令
        result = subprocess.run(cmd)
        return result.returncode
