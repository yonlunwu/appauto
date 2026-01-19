import json
import time
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

        if self.dataset.lower().startswith("aime"):
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

        background_cmd = f"nohup bash -c '{escaped_cmd}' > {log_file} 2>&1 & echo $! > {pid_file}"

        logger.info(f"Starting eval test in background, work_dir: {self.work_dir}")
        logger.info(f"Log file: {log_file}, PID file: {pid_file}")

        # 执行后台启动命令（立即返回）
        self.node.run(background_cmd, sudo=False, print_screen=False)

        return self.work_dir

    def check_eval_status(
        self, retry_log_check=3
    ) -> Tuple[Literal["running", "completed", "failed", "unknown"], Optional[str]]:
        """
        检查评估任务的当前运行状态 (State Machine Logic)。

        检测逻辑如下：
        1. **进程存活检查 (Process Liveness)**:
           优先检查 PID 进程是否在运行。如果存活，直接返回 "running"。

        2. **日志收尾校验 (Log Verification)**:
           如果进程已退出，进入“收尾校验”阶段。为了防止 NFS/IO 延迟导致日志未落盘，
           会进行 `retry_log_check` 次重试：
           - 扫描日志结尾，若包含 "Evaluation task completed" -> 判定为 "completed"。
           - 扫描日志结尾，若包含 "error" / "traceback" -> 判定为 "failed"。

        3. **兜底结果检查 (Fallback)**:
           如果日志分析未果，检查最终结果 JSON 文件是否存在。若存在 -> 判定为 "completed"。

        4. **未知状态 (Unknown)**:
           如果既无进程，也无日志结果，亦无 JSON 文件，判定为 "unknown"。
           (外层调用者应捕获此状态并继续轮询，而不是直接报错)。

        Args:
            retry_log_check (int): 进程退出后，读取日志的重试次数，防止 IO 延迟。

        Returns:
            Tuple[status, message]:
                - status: "running" | "completed" | "failed" | "unknown"
                - message: 状态描述信息
        """
        pid_file = f"/mnt/data/models/perftest/{self.work_dir}.pid"
        log_file = f"/mnt/data/models/perftest/{self.work_dir}.log"

        # 1. 检查进程是否还在运行
        rc, pid_output, _ = self.node.run(f"test -f {pid_file} && cat {pid_file}", sudo=False, silent=True)

        if rc == 0 and pid_output.strip():
            pid = pid_output.strip()
            # 检查 PID 是否存活
            rc_ps, _, _ = self.node.run(f"ps -p {pid}", sudo=False, silent=True)
            if rc_ps == 0:
                return "running", f"Process {pid} is running"


        success_keyword = "Evaluation task completed"

        for i in range(retry_log_check):
            # 读取日志最后 10 行
            rc, log_tail, _ = self.node.run(f"test -f {log_file} && tail -n 10 {log_file}", sudo=False, silent=True)

            if rc == 0 and log_tail:
                # 判定 A: 日志包含成功关键词
                if success_keyword in log_tail:
                    return "completed", "Log verified: Evaluation task completed"

                # 判定 B: 出现了明显的 Python 报错
                lower_tail = log_tail.lower()
                if "traceback" in lower_tail or "error" in lower_tail:
                    return "failed", f"Found error in log: {log_tail.splitlines()[-1]}"

            # 如果进程没了，但日志既没成功也没报错，可能是文件系统延迟，稍微等一下重试
            if i < retry_log_check - 1:
                time.sleep(2)

        # 2. 兜底检查：如果在日志里没找到，检查一下结果 JSON 文件是不是生成了
        # 有时候日志打印不全，但文件生成了也算成功
        result_file = f"/mnt/data/models/perftest/{self.work_dir}/*/reports/{self.model}/{self.dataset}.json"
        rc, _, _ = self.node.run(f"ls {result_file} 2>/dev/null", sudo=False, silent=True)
        if rc == 0:
            return "completed", "Result file found (Log verification skipped)"
        
        if rc_ps != 0:
            return "unknown", "Process not running and no result file found yet"

        # 3. 既没进程，也没日志成功标记，也没结果文件 -> 判定为失败
        return "unknown", "Unable to determine test status"

    def get_eval_progress(self) -> Optional[str]:
        """
        从日志文件获取当前测试进度信息

        Returns:
            Optional[str]: 进度信息（最后几行日志），如果无法获取则返回 None
        """
        log_file = f"/mnt/data/models/perftest/{self.work_dir}.log"

        rc, log_tail, _ = self.node.run(f"test -f {log_file} && tail -n 10 {log_file}", sudo=False, silent=True)

        if rc == 0 and log_tail:
            return log_tail.strip()

        return None

    def run_eval(self):
        """
        执行评测的主入口（异步启动 + 动态轮询模式）。
        
        流程：
        1. 通过 nohup 在远程后台启动评测任务。
        2. 进入 while 循环，定期轮询任务状态 (check_eval_status)。
        3. 处理网络波动（SSH异常）与 任务真实失败（RuntimeError）。
        4. 任务完成后拉取最终分数。
        """
        # 1. 后台启动任务
        self.start_eval_background()

        logger.info(f"Evaluation started in background. WorkDir: {self.work_dir}")
        logger.info("Waiting for evaluation to complete...")

        start_time = time.time()

        # 2. 动态轮询循环
        while True:
            # 检查超时
            if time.time() - start_time > self.timeout_s:
                raise TimeoutError(f"Evaluation timed out after {self.timeout_s} seconds")

            try:
                # 【修改】增加 try-except 容错
                # 如果这里的 SSH 发生 Connection reset 等网络波动，不会导致脚本直接炸掉
                status, msg = self.check_eval_status()

                if status == "running":
                    progress = self.get_eval_progress()
                    if progress:
                        logger.info(f"Eval Progress: {progress.splitlines()[-1]}")
                    time.sleep(30)

                elif status == "completed":
                    logger.info(f"Evaluation finished successfully: {msg}")
                    break

                elif status == "failed":
                    logger.error(f"Evaluation failed: {msg}")
                    raise RuntimeError(f"Evaluation task failed: {msg}")

                else:
                    logger.warning(f"Unknown status: {msg}, retrying...")
                    time.sleep(10)

            except Exception as e:
                if isinstance(e, RuntimeError) and "Evaluation task failed" in str(e):
                    raise e  # 真的失败了，往外抛

                # 网络波动等临时异常，打印 warning 并重试
                logger.warning(f"Error during status check (network fluctuation?): {str(e)}. Retrying in 10s...")
                time.sleep(10)

        # 3. 任务完成，获取分数并返回
        logger.info(f"Final Score: {self.score}")
        return self.score
        