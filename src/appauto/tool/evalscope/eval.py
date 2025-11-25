import json
from uuid import uuid4
from functools import cached_property
from typing import Dict, TYPE_CHECKING

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

    @cached_property
    def cmd(self):

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

        if "aime" in self.dataset.lower():
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

    # TODO 先探测, 没有再 download
    def download_script(self):
        cmd = (
            "curl -s -o /mnt/data/models/perftest/eval_via_es10x.py "
            "http://192.168.110.11:8090/scripts/eval_via_es10x.py"
        )
        self.node.run(cmd)

    def run_eval(self):
        """
        1. 下载脚本
        2. 生成 cmd 并执行测试(在宿主机执行测试)
        3. 从 work_dir 中读取 report_json 从而获取分数
        """
        self.download_script()
        self.node.run(self.cmd, sudo=False, print_screen=True)
        logger.info(f"score: {self.score}")
        return self.score
