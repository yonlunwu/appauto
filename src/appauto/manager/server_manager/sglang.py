from threading import Thread
from queue import Queue
from time import sleep
from typing import Literal, Tuple
from ..client_manager import BaseLinux
from ..utils_manager.network_utils import NetworkUtils


class SGLangServer(BaseLinux):
    def __init__(
        self,
        mgt_ip: str,
        conda_path: str,
        conda_env_name: str,
        model_path: Literal["DeepSeek-R1-GPTQ4-experts"],
        amx_weight_path: Literal["DeepSeek-R1-INT4"],
        served_model_name: Literal["DeepSeek-R1"],
        cpuinfer: int,
        context_length: int = 8192,
        max_running_request: int = 64,
        max_total_tokens: int = 65536,
        mem_fraction_static: float = 0.98,
        num_gpu_experts: int = 1,
        attention_backend: Literal["flashinfer"] = "flashinfer",
        trust_remote_code: bool = True,
        port=11002,
        host="0.0.0.0",
        disable_shared_experts_fusion=True,
        ssh_user="qujing",
        ssh_password="madsys123",
        ssh_port=22,
    ):
        super().__init__(mgt_ip, ssh_user, ssh_password, ssh_port)
        self.conda_path = conda_path
        self.conda_env_name = conda_env_name
        self.model_path = model_path
        self.amx_weight_path = amx_weight_path
        self.cpuinfer = cpuinfer
        self.num_gpu_experts = num_gpu_experts
        self.attention_backend = attention_backend
        self.trust_remote_code = trust_remote_code  # flag
        self.mem_fraction_static = mem_fraction_static
        self.context_length = context_length
        self.max_running_request = max_running_request
        self.max_total_tokens = max_total_tokens
        self.served_model_name = served_model_name
        self.port = int(port)
        self.host = host
        self.disable_shared_experts_fusion = disable_shared_experts_fusion  # flag

    def start(self, timeout_s=900) -> Tuple[Thread, Queue]:
        inner_cmd = (
            # TODO 遇到一个问题: ninja 不在 conda 环境下（which ninja）
            f"export PATH=$PATH:$HOME/.local/bin && "
            f"{self.conda_path} run -n {self.conda_env_name} python -m sglang.launch_server "
            f"--model /mnt/data/models/{self.model_path} "
            f"--amx-weight-path /mnt/data/models/{self.amx_weight_path} --cpuinfer {self.cpuinfer} "
            f"--num-gpu-experts {self.num_gpu_experts} --attention-backend {self.attention_backend} "
            f"--mem-fraction-static {self.mem_fraction_static} --context-length {self.context_length} "
            f"--max-running-requests {self.max_running_request} --max-total-tokens {self.max_total_tokens} "
            f"--served-model-name {self.served_model_name} --port {self.port} --host {self.host}"
        )

        if self.trust_remote_code:
            inner_cmd += " --trust-remote-code"

        if self.disable_shared_experts_fusion:
            inner_cmd += " --disable-shared-experts-fusion"

        cmd = f"bash -i -c '{inner_cmd}'"

        th, q = self.run_in_thread(cmd, sudo=False)

        NetworkUtils.wait_reachable(self.mgt_ip, self.port, interval_s=30, timeout_s=timeout_s)
        sleep(3)
        assert NetworkUtils.check_reachable(self.mgt_ip, self.port)

        return th, q

    def stop(self, interval_s=15, timeout_s=180, force=True):
        self.stop_process_by_keyword("sglang.launch_server", interval_s, timeout_s, force)
        sleep(3)
        assert not NetworkUtils.check_reachable(self.mgt_ip, self.port)

    def exist(self, keyword="sglang.launch_server"):
        return self.grep_pid(keyword)
