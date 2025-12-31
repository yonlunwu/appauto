import json
from uuid import uuid4
from functools import cached_property
from typing import Dict, TYPE_CHECKING, Literal, Optional, Tuple

if TYPE_CHECKING:
    from appauto.operator.amaas_node import AMaaSNodeCli
    from appauto.operator.amaas_node.cli.components.ft_ctn import FTContainer

from appauto.manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


class EvalscopeEval:
    def __init__(
        self,
        node: "AMaaSNodeCli",
        model: str,
        ip: str,
        port,
        dataset: str,
        max_tokens: int = 50000,
        concurrency: int = 4,
        limit: int = None,
        dataset_args: Dict = None,
        temperature: float = 0.6,
        enable_thinking=True,
        debug=True,
        timeout_s: int = 6000,
        work_dir: str = None,
        ft: "FTContainer" = None,
        api_key: str = None,
    ):
        self.node = node
        self.ft = ft
        self.model = model
        self.ip = ip
        self.port = port
        self.dataset = dataset
        self.max_tokens = max_tokens
        self.concurrency = concurrency
        self.limit = limit
        self.dataset_args = dataset_args
        self.temperature = temperature
        self.enable_thinking = enable_thinking
        self.debug = debug
        self.timeout_s = timeout_s
        self.work_dir = work_dir or str(uuid4())
        self.api_key = api_key

    def validate_env(self):
        self.node.run_with_check("test -d /mnt/data/models/perftest")
        self.node.run_with_check("test -f /mnt/data/models/perftest/venv/evalscope-py/bin/activate")
        self.node.run_with_check("test -f /mnt/data/models/perftest/eval_via_es10x.py")

    def validate_script(self):
        try:
            dst = "/mnt/data/models/perftest/eval_via_es10x.py"
            self.node.run_with_check(f"test -f {dst}")
            return "yes"
        except AssertionError:
            raise FileExistsError(f"{dst} not found.")

        except Exception as e:
            logger.error(f"error occurred while validating script: {str(e)}")
            raise e

    @cached_property
    def cmd(self):
        self.validate_env()
        prefix = "cd /mnt/data/models/perftest && source venv/evalscope-py/bin/activate && python eval_via_es10x.py"
        cmd = (
            prefix
            + f" --ip {self.ip} --port {self.port} --model {self.model} --datasets {self.dataset} "
            + f"--work-dir {self.work_dir} {'' if not self.api_key else f'--api-key {self.api_key} '}"
        )

        if self.limit:
            cmd += f" --limit {self.limit}"

        if self.concurrency:
            cmd += f" --concurrency {self.concurrency}"

        if self.max_tokens:
            cmd += f" --max-tokens {self.max_tokens}"

        if self.dataset.lower().startswith("aime24"):
            template = {
                "prompt_template": (
                    "{question}\nPlease reason step by step and place your final answer within boxed{{}}. "
                    "Force Requirement: 1.only the final answer should be wrapped in boxed{{}}; "
                    "2.no other numbers or text should be enclosed in boxed{{}}. 3.Answer in English"
                )
            }
            dataset_args = {self.dataset: template}

            cmd += f" --dataset-args '{json.dumps(dataset_args)}'"

        return cmd

    @cached_property
    def score(self):
        cmd = (
            f"cd /mnt/data/models/perftest/{self.work_dir} && grep -oP '\"score\":\s*\K[0-9.]+'  "
            f"./*/reports/{self.model}/{self.dataset}.json | head -n 1"
        )
        _, res, _ = self.node.run(cmd, sudo=False)
        return res

    # TODO 需要能连通 110.11
    def download_script(self):
        try:
            self.validate_script()
        except FileExistsError:
            cmd = (
                "curl -s -o /mnt/data/models/perftest/eval_via_es10x.py "
                "http://192.168.110.11:8090/scripts/eval_via_es10x.py"
            )
            self.node.run(cmd)

        except Exception as e:
            logger.error(f"error occurred while downloading script: {str(e)}")
            raise e

        finally:
            self.validate_script()

    def start_eval_background(self) -> str:
        """
        在远程机器后台启动 eval 测试，立即返回不等待结果

        Returns:
            str: work_dir 路径，用于后续查询进度和结果
        """
        self.download_script()

        # 构造后台执行命令（使用 nohup）
        log_file = f"/mnt/data/models/perftest/{self.work_dir}.log"
        pid_file = f"/mnt/data/models/perftest/{self.work_dir}.pid"

        # 转义命令中的单引号，避免嵌套引号冲突
        escaped_cmd = self.cmd.replace("'", "'\"'\"'")

        background_cmd = (
            f"nohup bash -c '{escaped_cmd}' > {log_file} 2>&1 & echo $! > {pid_file}"
        )

        logger.info(f"Starting eval test in background, work_dir: {self.work_dir}")
        logger.info(f"Log file: {log_file}, PID file: {pid_file}")

        # 执行后台启动命令（立即返回）
        self.node.run(background_cmd, sudo=False, print_screen=False)

        return self.work_dir

    def check_eval_status(self) -> Tuple[Literal["running", "completed", "failed", "unknown"], Optional[str]]:
        """
        检查 eval 测试的运行状态

        Returns:
            Tuple[status, message]:
                - status: "running", "completed", "failed", "unknown"
                - message: 状态说明信息
        """
        pid_file = f"/mnt/data/models/perftest/{self.work_dir}.pid"
        result_file = f"/mnt/data/models/perftest/{self.work_dir}/*/reports/{self.model}/{self.dataset}.json"

        # 1. 检查进程是否还在运行
        rc, pid_output, _ = self.node.run(f"test -f {pid_file} && cat {pid_file}", sudo=False, silent=True)

        if rc == 0 and pid_output.strip():
            pid = pid_output.strip()
            rc_ps, _, _ = self.node.run(f"ps -p {pid}", sudo=False, silent=True)

            if rc_ps == 0:
                # 进程还在运行
                return "running", f"Process {pid} is still running"

        # 2. 检查结果文件是否存在
        rc, _, _ = self.node.run(f"ls {result_file} 2>/dev/null", sudo=False, silent=True)

        if rc == 0:
            # 结果文件存在，测试已完成
            return "completed", "Result file found, test completed"

        # 3. 检查日志文件中是否有错误
        log_file = f"/mnt/data/models/perftest/{self.work_dir}.log"
        rc, log_tail, _ = self.node.run(
            f"test -f {log_file} && tail -n 50 {log_file}",
            sudo=False,
            silent=True
        )

        if rc == 0 and log_tail:
            # 进程不在运行且无结果文件，检查是否有错误
            if "error" in log_tail.lower() or "exception" in log_tail.lower() or "failed" in log_tail.lower():
                return "failed", f"Test failed, check log: {log_file}"
            elif "traceback" in log_tail.lower():
                return "failed", f"Test failed with exception, check log: {log_file}"

        # 4. 如果进程不在运行，也没有结果，可能是刚启动或已失败
        if rc_ps != 0:
            return "unknown", "Process not running and no result file found yet"

        return "unknown", "Unable to determine test status"

    def get_eval_progress(self) -> Optional[str]:
        """
        从日志文件获取当前测试进度信息

        Returns:
            Optional[str]: 进度信息（最后几行日志），如果无法获取则返回 None
        """
        log_file = f"/mnt/data/models/perftest/{self.work_dir}.log"

        rc, log_tail, _ = self.node.run(
            f"test -f {log_file} && tail -n 10 {log_file}",
            sudo=False,
            silent=True
        )

        if rc == 0 and log_tail:
            return log_tail.strip()

        return None

    def run_eval(self):
        """
        原有的同步执行方法（保持向后兼容）
        1. 下载脚本
        2. 生成 cmd 并执行测试(在宿主机执行测试)
        3. 从 work_dir 中读取 report_json 从而获取分数
        """
        self.download_script()
        self.node.run(self.cmd, sudo=False, print_screen=True)
        logger.info(f"score: {self.score}")
        return self.score
