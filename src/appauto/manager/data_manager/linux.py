from typing import List
from dataclasses import dataclass

# 定义 GPU 空闲判断的阈值
MEM_THRESHOLD = 5.0  # 显存使用率低于 5%
COMPUTE_THRESHOLD = 5  # 计算利用率低于 5%


@dataclass
class GPUInstance:
    """用于存储单个 GPU 状态摘要。"""

    id: int  # GPU 索引 (e.g., 0, 1)
    name: str  # GPU 名称 (e.g., 'NVIDIA GeForce RTX 3090')
    total_mem_mib: int  # 总显存 (MiB)
    used_mem_mib: int  # 已用显存 (MiB)
    mem_util: float  # 显存使用率 (%)
    compute_util: int  # 计算利用率 (%)
    is_idle: bool  # 是否空闲

    def __str__(self):
        return (
            f"[GPU {self.id}] {self.name},"
            f"  is_idle: {self.is_idle},"
            f"  used_mem_mib/total: {self.used_mem_mib} MiB / {self.total_mem_mib} MiB,"
            f"  mem_util: {self.mem_util:.2f}%,"
            f"  compute_util: {self.compute_util}%"
        )


@dataclass
class GPUsOverallView:
    """用于存储整体 GPU 情况统计。"""

    total_gpus: int  # 总 GPU 数量
    idle_gpus: int  # 空闲 GPU 数量
    busy_gpus: int  # 忙碌 GPU 数量
    instances: List[GPUInstance]  # 每个 GPU 的详细信息列表

    def get_idle_summaries(self) -> List[GPUInstance]:
        """获取所有空闲 GPU 的详细信息列表。"""
        return [s for s in self.instances if s.is_idle]

    def get_busy_summaries(self) -> List[GPUInstance]:
        """获取所有忙碌 GPU 的详细信息列表。"""
        return [s for s in self.instances if not s.is_idle]

    def __str__(self):
        return f"total: {self.total_gpus}, free: {self.idle_gpus} busy: {self.busy_gpus}"
