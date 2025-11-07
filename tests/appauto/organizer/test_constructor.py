from appauto.organizer.constructor import ModelParams
from appauto.manager.config_manager.config_logging import LoggingConfig


logger = LoggingConfig.get_logger()


class TestModelParams:
    def test_nvidia_deepseek_r1_0528_correct_2tp_cmd(self):
        model_params = ModelParams(
            node="node1", engine="ft", model_name="DeepSeek-R1-0528-GPU-weight", tp=2, mode="correct"
        )
        cmd = model_params.as_cmd
        logger.info(cmd)

        assert "ftransformers.launch_server" in cmd
        assert "--model-path /mnt/data/models/DeepSeek-R1-0528-GPU-weight" in cmd
        assert "--served-model-name DeepSeek-R1-0528-GPU-weight" in cmd
        assert "--tensor-parallel-size 2" in cmd
        assert "--max-running-requests 50" in cmd
        assert "--max-total-tokens 50000" in cmd

    def test_nvidia_deepseek_r1_0528_perf_1tp_cmd(self):
        model_params = ModelParams(
            node="node1", engine="sglang", model_name="DeepSeek-R1-0528-GPU-weight", tp=1, mode="perf"
        )
        cmd = model_params.as_cmd
        logger.info(cmd)

        assert "sglang.launch_server" in cmd
        assert "--model-path /mnt/data/models/DeepSeek-R1-0528-GPU-weight" in cmd
        assert "--served-model-name DeepSeek-R1-0528-GPU-weight" in cmd
        assert "--tensor-parallel-size 1" in cmd
        assert "--max-running-requests 37" in cmd
        assert "--max-total-tokens 37000" in cmd
        assert "--num-gpu-experts 10" in cmd
        assert "--dp" not in cmd
