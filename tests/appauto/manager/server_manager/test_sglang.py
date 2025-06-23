from appauto.manager.server_manager import SGLangServer
from appauto.manager.config_manager import LoggingConfig
from appauto.manager.utils_manager.network_utils import NetworkUtils


logger = LoggingConfig.get_logger()

sglang = SGLangServer(
    mgt_ip="192.168.110.15",
    conda_path="/home/zkyd/miniconda3/bin/conda",
    conda_env_name="yanlong-ft",
    model_path="DeepSeek-R1-GPTQ4-experts",
    amx_weight_path="DeepSeek-R1-INT4",
    served_model_name="DeepSeek-R1",
    cpuinfer=80,
    ssh_user="zkyd",
    ssh_password="zkyd@12#$",
)


class TestSGLangServer:
    def test_sglang_start(self):
        sglang.start()
        assert sglang.exist(keyword="sglang.launch_server")
        assert NetworkUtils.check_reachable(sglang.mgt_ip, sglang.port)
        assert sglang.exist(keyword="sglang.launch_server")

    def test_sglang_stop(self):
        assert sglang.exist(keyword="sglang.launch_server")
        sglang.stop()
        assert not sglang.exist(keyword="sglang.launch_server")
