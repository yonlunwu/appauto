"""
基于 ft container 做测试, name 固定为 zhiwen-ft
"""

import time
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, Literal, Tuple, Dict
from appauto.organizer.model_params.constructor import FTModelParams
from appauto.manager.client_manager import BaseDockerContainer
from appauto.manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()

if TYPE_CHECKING:
    from ..amaas_node_cli import AMaaSNodeCli


class FTContainer(BaseDockerContainer):
    def __init__(
        self,
        node: "AMaaSNodeCli",
        name: str = "zhiwen-ft",
        conda_path="/root/miniforge3/bin/conda",
        conda_env="ftransformers",
        engine="ftransformers",
    ):
        super().__init__(node, name)
        self.conda_path = conda_path
        self.conda_env = conda_env
        self.engine = engine

    def launch_model(
        self,
        model_name: str,
        tp: int,
        mode: Literal["correct", "perf", "mtp_correct", "mtp_perf"] = "correct",
        port=30000,
        sudo=False,
        wait_for_running=True,
        interval_s=20,
        timeout_s=900,
        print_screen=True,
    ):
        """
        nohup 启动模型并将模型日志重定向至指定路径。
        """
        cmd = (
            f"source /root/miniforge3/etc/profile.d/conda.sh && conda activate {self.conda_env} && "
            f"{FTModelParams(self.node, 'ft', model_name, tp, mode, port).as_cmd}"
        )
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        nohup_cmd = f'nohup bash -c "{cmd} > /tmp/{model_name}_{timestamp}.log 2>&1 &"'

        logger.info(f"[{self.engine}] launch model: {model_name}, log: /tmp/{model_name}_{timestamp}.log")
        rc, res, err = self.run(nohup_cmd, sudo, print_screen)

        if wait_for_running:
            self.wait_model_to_running(port, interval_s, timeout_s)

        return rc, res, err

    def launch_model_in_thread(
        self,
        model_name: str,
        tp: int,
        mode: Literal["correct", "perf", "mtp_correct", "mtp_perf"] = "correct",
        port=30000,
        wait_for_running=True,
        interval_s=20,
        timeout_s=900,
        sudo=True,
    ) -> Tuple[Queue, Thread]:

        cmd = (
            f"source /root/miniforge3/etc/profile.d/conda.sh && conda activate {self.conda_env} && "
            f"{FTModelParams(self.node, 'ft', model_name, tp, mode, port).as_cmd}"
        )
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        nohup_cmd = f'nohup bash -c "{cmd} > /tmp/{model_name}_{timestamp}.log 2>&1 &"'

        logger.info(f"[{self.engine}] launch model: {model_name}, log: /tmp/{model_name}_{timestamp}.log")

        th, q = self.run_in_thread(nohup_cmd, sudo, True, True)

        if wait_for_running:
            self.wait_model_to_running(port, interval_s, timeout_s)

        return th, q

    def stop_model(self, model_name) -> bool:
        """
        主动停止指定模型
        """
        logger.info(f"stop model: {model_name}")
        self.node.stop_process_by_keyword(self.engine, model_name, force=True)

    def run_eval_via_evalscope(
        self,
        port: int,
        model: str,
        dataset: str,
        max_tokens: int = 50000,
        concurrency: int = 4,
        limit: int = None,
        dataset_args: Dict = None,
        temperature: float = 0.6,
        enable_thinking: bool = True,
        debug: bool = True,
        timeout_s: int = 6000,
    ):
        from appauto.tool.evalscope.eval import EvalscopeEval

        evalscope = EvalscopeEval(
            self.node,
            model,
            self.ip,
            port,
            dataset,
            max_tokens,
            concurrency,
            limit,
            dataset_args,
            temperature,
            enable_thinking,
            debug,
            timeout_s,
            ft=self,
        )
        evalscope.run_eval()
        logger.info(f"score: {evalscope.score}")
        return evalscope.score

    def run_perf_via_evalscope(
        self,
        port: int,
        model: str,
        parallel: str = "1 4",
        number: str = "1 4",
        input_length=128,
        output_length=512,
        read_timeout=600,
        seed=42,
        loop=1,
        name="appauto-bench",
        debug=False,
    ):
        from appauto.tool.evalscope.perf import EvalscopePerf

        evalscope = EvalscopePerf(
            self.node,
            model,
            self.ip,
            port,
            parallel,
            number,
            f"/mnt/data/models/{model}",
            "EMPTY",
            input_length,
            output_length,
            read_timeout,
            seed,
            loop,
            name,
            debug,
            self,
        )
        evalscope.run_perf()
