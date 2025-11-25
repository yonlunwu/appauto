from uuid import uuid4
from datetime import datetime
from typing import TYPE_CHECKING
from functools import cached_property

if TYPE_CHECKING:
    from appauto.operator.amaas_node import AMaaSNodeCli
    from appauto.operator.amaas_node.cli.components.ft_ctn import FTContainer


from appauto.manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


class EvalscopePerf:
    def __init__(
        self,
        node: "AMaaSNodeCli",
        model: str,
        ip: str,
        port: int,
        parallel: str,
        number: str,
        tokenizer_path,
        api_key=None,
        input_length=128,
        output_length=512,
        read_timeout=600,
        seed=42,
        loop=1,
        name="appauto-bench",
        debug=False,
        ft: "FTContainer" = None,
    ):
        self.node = node
        self.ft = ft
        self.model = model
        self.ip = ip
        self.port = port
        self.parallel = parallel
        self.number = number
        self.tokenizer_path = tokenizer_path
        self.api_key = api_key
        self.input_length = input_length
        self.output_length = output_length
        self.output_csv = f'{str(uuid4())}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        self.read_timeout = read_timeout
        self.seed = seed
        self.loop = loop
        self.name = name
        self.debug = debug

    @cached_property
    def cmd(self):
        prefix = "cd /mnt/data/models/perftest && source venv/evalscope-py/bin/activate && python perf_via_es10x.py"
        cmd = (
            prefix + f" --ip {self.ip} --port {self.port} --parallel {self.parallel} --number {self.number} "
            f"{'' if not self.api_key else f'--api-key {self.api_key} '}"
            f"--model {self.model} --tokenizer-path {self.tokenizer_path} --input-length {self.input_length} "
            f"--output-length {self.output_length} --read-timeout {self.read_timeout} --seed {self.seed} "
            f"--loop {self.loop} --output-csv {self.output_csv} "
        )

        return cmd

    # TODO 先探测, 没有再 download
    def download_script(self):
        cmd = (
            "curl -s -o /mnt/data/models/perftest/perf_via_es10x.py "
            "http://192.168.110.11:8090/scripts/perf_via_es10x.py"
        )
        self.node.run(cmd)

    def run_perf(self):
        """
        1. 下载脚本
        2. 生成 cmd 并执行测试(在宿主机执行测试)
        3. 将生成的 xlsx 文件 download 到本地
        """
        self.download_script()
        self.node.run(self.cmd, sudo=False, print_screen=True)
        logger.info(f"The performance test data has been saved to: {self.output_csv}.csv, {self.output_csv}.xlsx")
        self.node.download(f"/mnt/data/models/perftest/{self.output_csv}.xlsx", f"{self.output_csv}.xlsx")
