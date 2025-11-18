# TODO python 不能写死，需要知道 conda env 下的 python path
# TODO 是否能在测试机器上固定 conda env python path?
SGLANG_PREFIX = (
    "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python -m sglang.launch_server --host 0.0.0.0 --port {}"
)
# FT_PREFIX = "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python -m ftransformers.launch_server"
FT_PREFIX = "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True /root/miniforge3/envs/ftransformers/bin/python -m ftransformers.launch_server --host 0.0.0.0 --port {}"
